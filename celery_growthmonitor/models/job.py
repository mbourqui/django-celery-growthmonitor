from __future__ import absolute_import, unicode_literals

import logging
import os
import random as rnd
import re
from datetime import datetime
from distutils.version import StrictVersion
from enum import unique

from django import get_version as django_version
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .. import settings

logger = logging.getLogger(__name__)
TEMPORARY_JOB_FOLDER = "tmp"


def job_root(instance, filename=""):
    """
    Return the path of `filename` stored at the root folder of his job `instance`.

    Parameters
    ----------
    instance : AJob
        The model instance associated with the file
    filename : str
        Original filename

    Returns
    --------
    str
        Path to the root folder for that job
    """
    if instance.root_job:
        if callable(instance.root_job):
            return os.path.join(settings.APP_MEDIA_ROOT, instance.root_job())
        else:
            head = str(instance.root_job)
    else:
        head = instance.__class__.__name__.lower()
    if not instance.id or (
        instance.id
        and getattr(instance, "_tmp_id", None)
        and not getattr(instance, "_tmp_files", None)
    ):
        tail = os.path.join(TEMPORARY_JOB_FOLDER, str(getattr(instance, "_tmp_id")))
    else:
        tail = str(instance.id)
    return os.path.join(settings.APP_MEDIA_ROOT, head, tail, filename)


def job_data(instance, filename=""):
    """
    Return the path of `filename` stored in a subfolder of the root folder of his job `instance`.

    Parameters
    ----------
    instance : AJob or ADataFile
        The model instance associated
    filename : str
        Original filename

    Returns
    --------
    str
        Path to filename which is unique for a job
    """
    job = instance if isinstance(instance, AJob) else instance.job
    head = job.upload_to_root()
    tail = os.path.join("data", filename)
    return os.path.join(head, tail)


def job_results(instance, filename=""):
    """
    Return the path of `filename` stored in a subfolder of the root folder of his job `instance`.

    Parameters
    ----------
    instance : AJob or ADataFile
        The model instance associated
    filename : str
        Original filename

    Returns
    --------
    str
        Path to filename which is unique for a job
    """
    job = instance if isinstance(instance, AJob) else instance.job
    head = job.upload_to_root()
    tail = os.path.join("results", filename)
    return os.path.join(head, tail)


def get_upload_to_path(instance, callable_or_prefix, filename=""):
    """

    Parameters
    ----------
    instance : AJob or ADataFile
        The model instance associated
    callable_or_prefix
    filename : str

    Returns
    -------
    str
        Path as would be provided to the `upload_to` parameter

    """
    if callable(callable_or_prefix):
        # It's a callable attribute
        return callable_or_prefix(filename)
    else:
        # It's a prefix
        job = instance if isinstance(instance, AJob) else instance.job
        return os.path.join(job.upload_to_root(), callable_or_prefix, filename)


def get_absolute_path(instance, callable_or_prefix, filename=""):
    """

    Parameters
    ----------
    instance : AJob or ADataFile
        The model instance associated
    callable_or_prefix
    filename : str

    Returns
    -------
    str
        Absolute path to the file

    """
    return os.path.join(
        settings.django_settings.MEDIA_ROOT,
        get_upload_to_path(instance, callable_or_prefix, filename),
    )


class AJob(models.Model):
    """

    Set `root_job` to define a custom root path (str or callable).
    Set `upload_to_root` to define a custom path to the root folder of the job (str or callable).
    Set `upload_to_results` to define a custom path to the results sub-folder of the job (str or callable).
    Set ``REQUIRED_USER_FILES_ATTRNAME`` to define mandatory files uploaded with this job (or use ADataFile if multiple)

    --------
    http://stackoverflow.com/questions/16655097/django-abstract-models-versus-regular-inheritance#16838663
    """

    from autoslug import AutoSlugField
    from echoices.enums import EChoice
    from echoices.fields import make_echoicefield

    class Meta:
        abstract = True

    @unique
    class EState(EChoice):
        # Creation codes
        CREATED = (0, "Created")
        # Submission codes
        SUBMITTED = (10, "Submitted")
        # Computation codes
        RUNNING = (20, "Running")
        # Completion codes
        COMPLETED = (30, "Completed")

    @unique
    class EStatus(EChoice):
        ACTIVE = (0, "Active")
        SUCCESS = (10, "Succeeded")
        FAILURE = (20, "Failed")

    IDENTIFIER_MIN_LENGTH = 0
    IDENTIFIER_MAX_LENGTH = 32
    IDENTIFIER_ALLOWED_CHARS = "[a-zA-Z0-9]"
    IDENTIFIER_REGEX = re.compile(
        "{}{{{},}}".format(IDENTIFIER_ALLOWED_CHARS, IDENTIFIER_MIN_LENGTH)
    )
    SLUG_MAX_LENGTH = 32
    SLUG_RND_LENGTH = 6

    REQUIRED_USER_FILES_ATTRNAME = "required_user_files"

    root_job = None
    upload_to_root = job_root
    upload_to_results = job_results

    def slug_default(self):
        if self.identifier:
            slug = self.identifier[: min(len(self.identifier), self.SLUG_RND_LENGTH)]
        else:
            slug = self.__class__.__name__[0]
        slug += self.timestamp.strftime("%y%m%d%H%M")  # YYMMDDHHmm
        if len(slug) > self.SLUG_MAX_LENGTH:
            slug = slug[: self.SLUG_MAX_LENGTH - self.SLUG_RND_LENGTH] + str(
                rnd.randrange(
                    10 ** (self.SLUG_RND_LENGTH - 1), 10 ** self.SLUG_RND_LENGTH
                )
            )
        # TODO: assert uniqueness, otherwise regen
        return slug

    timestamp = models.DateTimeField(
        verbose_name=_("job creation timestamp"), auto_now_add=True
    )
    # TODO: validate identifier over allowance for slug or [a-zA-Z0-9_]
    identifier = models.CharField(
        max_length=IDENTIFIER_MAX_LENGTH,
        blank=True,
        db_index=True,
        help_text=_("Human readable identifier, as provided by the submitter"),
        validators=[RegexValidator(regex=IDENTIFIER_REGEX)],
    )
    slug = AutoSlugField(
        db_index=True,
        editable=True,
        help_text=_(
            "Human readable url, must be unique, a default one will be generated if none is given"
        ),
        max_length=SLUG_MAX_LENGTH,
        populate_from=slug_default,
        unique=True,
    )
    state = make_echoicefield(EState, default=EState.CREATED, editable=False)
    status = make_echoicefield(EStatus, default=EStatus.ACTIVE, editable=False)
    started = models.DateTimeField(null=True, editable=False)
    duration = models.DurationField(null=True, editable=False)
    closure = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text=_(
            "Timestamp of removal, will be set automatically on creation if not given"
        ),
    )  # Default is set on save()
    error = models.TextField(null=True, editable=False)

    def __str__(self):
        return str(
            "{} {} ({} and {})".format(
                self.__class__.__name__, self.id, self.state.label, self.status.label
            )
        )

    def _move_data_from_tmp_to_upload(self):
        # https://stackoverflow.com/a/16574947/
        # TODO: assert required_user_files is not empty? --> user warning?
        setattr(
            self, "_tmp_files", list(getattr(self, self.REQUIRED_USER_FILES_ATTRNAME))
        )
        for field in getattr(self, self.REQUIRED_USER_FILES_ATTRNAME):
            file = (
                getattr(self, field)
                if isinstance(field, str)
                else getattr(self, field.attname)
            )
            if not file:
                raise FileNotFoundError(
                    "{} is indicated as required, but no file could be found".format(
                        field
                    )
                )
            # Create new filename, using primary key and file extension
            old_filename = file.name
            new_filename = file.field.upload_to(self, os.path.basename(old_filename))
            # TODO: try this instead: https://docs.djangoproject.com/en/1.11/topics/files/#using-files-in-models
            # Create new file and remove old one
            file.storage.save(new_filename, file)
            file.name = new_filename
            file.close()
            file.storage.delete(old_filename)
            getattr(self, "_tmp_files").remove(field)
        import shutil

        shutil.rmtree(get_absolute_path(self, self.upload_to_root))
        setattr(self, "_tmp_id", 0)

    def save(self, *args, results_exist_ok=False, **kwargs):
        created = not self.pk
        if created and getattr(self, "required_user_files", []):
            setattr(self, "upload_to_data", getattr(self, "upload_to_data", None))
            setattr(self, "_tmp_id", rnd.randrange(10 ** 6, 10 ** 7))
        try:
            super(AJob, self).save(*args, **kwargs)  # Call the "real" save() method.
        except AttributeError as ae:
            if "object has no attribute '_tmp_id'" in str(ae.args):
                raise AttributeError(
                    "It looks like you forgot to set the `required_user_files` attribute on {}.".format(
                        self.__class__
                    )
                ) from None
            raise ae
        if created:
            dirty = False
            if settings.TTL.seconds > 0:
                # Set timeout
                self.closure = self.timestamp + settings.TTL
                dirty = True  # Write closure to DB
            if getattr(self, "required_user_files", []):
                self._move_data_from_tmp_to_upload()
                dirty = True  # Persist file changes
            if dirty:
                super(AJob, self).save()
            # Ensure the destination folder exists (may create some issues else, depending on application usage)
            os.makedirs(
                get_absolute_path(self, self.upload_to_results),
                exist_ok=results_exist_ok,
            )

    def progress(self, new_state):
        """
        Signal a change in the pipeline

        Parameters
        ----------
        new_state : EState

        Returns
        -------
        EState
            The previous state

        """
        old_state = self.state
        self.state = new_state
        self.save()
        return old_state

    def start(self):
        """
        To be called when the job is to be started.

        Returns
        -------
        state : EState
        status : EStatus
        started : datetime

        """
        self.started = timezone.now()
        self.progress(self.EState.RUNNING)
        logger.debug("Starting {} at {}".format(self, self.started))
        return self.state, self.status, self.started

    def stop(self):
        """
        To be called when the job is completed. Can be called multiple times, will only be applied once.

        Returns
        -------
        state : EState
        status : EStatus
        duration : datetime.timedelta
            Duration of the job

        """
        self._set_duration()
        if self.state is not self.EState.COMPLETED:
            self.status = (
                self.EStatus.FAILURE if self.has_failed() else self.EStatus.SUCCESS
            )
            self.progress(self.EState.COMPLETED)  # This will also save the job
            logger.debug(
                "{} terminated in {}s with status '{}'".format(
                    self, self.duration, self.status.label
                )
            )
        return self.state, self.status, self.duration

    def failed(self, task, exception):
        """
        Mark the job as failed and stop it.

        Note that it may not stop the chain, though.

        Parameters
        ----------
        task
        exception

        Returns
        -------
        TODO

        """
        self._set_duration()
        from json import dumps

        self.error = dumps(
            dict(
                task=task.__name__,
                exception="{}".format(type(exception).__name__),
                msg="{}".format(exception),
            )
        )
        # TODO: http://stackoverflow.com/questions/4564559/
        logger.exception(
            "Task %s failed with following exception: %s", task.__name__, exception
        )
        return self.stop()

    def has_failed(self):
        return bool(self.error)

    def _set_duration(self):
        if not self.duration:
            self.duration = timezone.now() - self.started
            self.save()
        return self.duration


class ADataFile(models.Model):
    class Meta:
        abstract = True

    upload_to_data = job_data

    job = None  # Just a placeholder for IDEs
    data = None  # Just a placeholder for IDEs

    if StrictVersion(django_version()) < StrictVersion("1.10.0"):
        # SEE: https://docs.djangoproject.com/en/1.10/topics/db/models/#field-name-hiding-is-not-permitted
        job = None  # Just a placeholder, Django < 1.10 does not support overriding Fields of abstract models
        data = None  # Just a placeholder, Django  < 1.10 does not support overriding Fields of abstract models
    else:
        job = models.ForeignKey(
            AJob, on_delete=models.CASCADE
        )  # placeholder, must be overridden by concrete class
        data = models.FileField(upload_to=upload_to_data, max_length=256)


@receiver(models.signals.post_delete,)
def _autoremove_files(sender, instance, *args, **kwargs):
    """
    Make sure we remove the files form the filesystem.

    Parameters
    ----------
    sender
    instance
    args
    kwargs

    """
    if issubclass(sender, AJob):
        if hasattr(instance, instance.REQUIRED_USER_FILES_ATTRNAME):
            for field in getattr(instance, instance.REQUIRED_USER_FILES_ATTRNAME):
                file = (
                    getattr(instance, field)
                    if isinstance(field, str)
                    else getattr(instance, field.attname)
                )
                file.delete(save=False)
        # Delete all remaining files stored on the filesystem
        import shutil

        shutil.rmtree(get_absolute_path(instance, instance.upload_to_root))
    elif issubclass(sender, ADataFile):
        instance.data.delete(save=False)
