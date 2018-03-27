import logging
import os
import random as rnd
import re
from datetime import datetime
from distutils.version import StrictVersion
from enum import unique

from autoslug import AutoSlugField
from django import get_version as django_version
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .. import settings

logger = logging.getLogger(__name__)
TEMPORARY_JOB_FOLDER = 'tmp'


def _user_path(attribute_or_prefix, filename=''):
    if attribute_or_prefix:
        if callable(attribute_or_prefix):
            # It's a callable attribute
            co_code = attribute_or_prefix.__code__.co_code
            if co_code != job_data.__code__.co_code and co_code != job_results.__code__.co_code:
                # Prevent infinite recursion if using job_data(...) or job_results(...)
                return attribute_or_prefix(filename)
        else:
            # It's a prefix
            return os.path.join(attribute_or_prefix, filename)
    return None


def root_job(instance):
    """
    Return the root path in the filesystem for the job `instance` folder.

    Parameters
    ----------
    instance : AJob
        The model instance associated with the file

    Returns
    --------
    str
        Path to the root folder for that job
    """
    if instance.job_root:
        if callable(instance.job_root):
            return os.path.join(settings.APP_MEDIA_ROOT, instance.job_root())
        else:
            head = str(instance.job_root)
    else:
        head = instance.__class__.__name__.lower()
    if not instance.id or (
                    instance.id and getattr(instance, '_tmp_id', None) and not getattr(instance, '_tmp_files', None)):
        tail = os.path.join(TEMPORARY_JOB_FOLDER, str(getattr(instance, '_tmp_id')))
    else:
        tail = str(instance.id)
    return os.path.join(settings.APP_MEDIA_ROOT, head, tail)


def job_root(instance, filename=''):
    """
    Return the path of `filename` stored at the root folder of his job `instance`.

    Parameters
    ----------
    instance : AJob
        The model instance associated
    filename : str
        Original filename

    Returns
    --------
    str
        Path to filename which is unique for a job
    """
    return os.path.join(root_job(instance), filename)


def job_data(instance, filename=''):
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
    head = root_job(instance.job) if isinstance(instance, ADataFile) else root_job(instance)
    tail = _user_path(instance.upload_to_data, filename) or os.path.join('data', filename)
    return os.path.join(head, tail)


def job_results(instance, filename=''):
    """
    Return the path of `filename` stored in a subfolder of the root folder of his job `instance`.

    Parameters
    ----------
    instance : AJob
        The model instance associated
    filename : str
        Original filename

    Returns
    --------
    str
        Path to filename which is unique for a job
    """
    tail = _user_path(instance.upload_to_results, filename) or os.path.join('results', filename)
    return os.path.join(root_job(instance), tail)


class AJob(models.Model):
    """
    See Also
    --------
    http://stackoverflow.com/questions/16655097/django-abstract-models-versus-regular-inheritance#16838663
    """

    from echoices.enums import EChoice
    from echoices.fields import make_echoicefield

    class Meta:
        abstract = True

    @unique
    class EStates(EChoice):
        # Creation codes
        CREATED = (0, 'Created')
        # Submission codes
        SUBMITTED = (100, 'Submitted')
        # Computation codes
        RUNNING = (200, 'Running')
        # Completion codes
        COMPLETED = (300, 'Completed')

    @unique
    class EStatuses(EChoice):
        ACTIVE = (0, 'Active')
        SUCCESS = (10, 'Succeeded')
        FAILURE = (20, 'Failed')

    IDENTIFIER_MIN_LENGTH = 0
    IDENTIFIER_MAX_LENGTH = 32
    IDENTIFIER_ALLOWED_CHARS = "[a-zA-Z0-9]"
    IDENTIFIER_REGEX = re.compile("{}{{{},}}".format(IDENTIFIER_ALLOWED_CHARS, IDENTIFIER_MIN_LENGTH))
    SLUG_MAX_LENGTH = 32
    SLUG_RND_LENGTH = 6

    job_root = None
    upload_to_results = None

    def slug_default(self):
        if self.identifier:
            slug = self.identifier[:min(len(self.identifier), self.SLUG_RND_LENGTH)]
        else:
            slug = self.__class__.__name__[0]
        slug += self.timestamp.strftime("%y%m%d%H%M")  # YYMMDDHHmm
        if len(slug) > self.SLUG_MAX_LENGTH:
            slug = slug[:self.SLUG_MAX_LENGTH - self.SLUG_RND_LENGTH] + \
                   str(rnd.randrange(10 ** (self.SLUG_RND_LENGTH - 1), 10 ** self.SLUG_RND_LENGTH))
        # TODO: assert uniqueness, otherwise regen
        return slug

    timestamp = models.DateTimeField(verbose_name=_("job creation timestamp"), auto_now_add=True)
    # TODO: validate identifier over allowance for slug or [a-zA-Z0-9_]
    identifier = models.CharField(
        max_length=IDENTIFIER_MAX_LENGTH,
        blank=True,
        db_index=True,
        help_text=_("Human readable identifier, as provided by the submitter"),
        validators=[RegexValidator(regex=IDENTIFIER_REGEX)])
    slug = AutoSlugField(
        db_index=True,
        editable=True,
        help_text=_("Human readable url, must be unique, a default one will be generated if none is given"),
        max_length=SLUG_MAX_LENGTH,
        populate_from=slug_default,
        unique=True)
    state = make_echoicefield(EStates, default=EStates.CREATED, editable=False)
    status = make_echoicefield(EStatuses, default=EStatuses.ACTIVE, editable=False)
    started = models.DateTimeField(null=True, editable=False)
    duration = models.DurationField(null=True, editable=False)
    error = models.TextField(null=True, editable=False)
    closure = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text=_("Timestamp of removal, will be set automatically on creation if not given")
    )  # Default is set on save()

    def __str__(self):
        return str('{} {} ({} and {})'.format(self.__class__.__name__, self.id, self.state.label, self.status.label))

    def _move_data_from_tmp_to_upload(self):
        # https://stackoverflow.com/a/16574947/
        # TODO: assert required_user_files is not empty? --> user warning?
        setattr(self, '_tmp_files', list(getattr(self, 'required_user_files')))
        for field in self.required_user_files:
            file = getattr(self, field) if isinstance(field, str) else getattr(self, field.attname)
            if not file:
                raise FileNotFoundError("{} is indicated as required, but no file could be found".format(field))
            # Create new filename, using primary key and file extension
            old_filename = file.name
            new_filename = file.field.upload_to(self, os.path.basename(old_filename))
            # TODO: try this instead: https://docs.djangoproject.com/en/1.11/topics/files/#using-files-in-models
            # Create new file and remove old one
            file.storage.save(new_filename, file)
            file.name = new_filename
            file.close()
            file.storage.delete(old_filename)
            getattr(self, '_tmp_files').remove(field)
        import shutil
        shutil.rmtree(os.path.join(settings.django_settings.MEDIA_ROOT, root_job(self)))
        setattr(self, '_tmp_id', 0)

    def save(self, *args, results_exist_ok=False, **kwargs):
        created = not self.pk
        if created and getattr(self, 'required_user_files', []):
            setattr(self, 'upload_to_data', getattr(self, 'upload_to_data', None))
            setattr(self, '_tmp_id', rnd.randrange(10 ** 6, 10 ** 7))
        try:
            super(AJob, self).save(*args, **kwargs)  # Call the "real" save() method.
        except AttributeError as ae:
            if "object has no attribute '_tmp_id'" in str(ae.args):
                raise AttributeError(
                    "It looks like you forgot to set the `required_user_files` attribute on {}.".format(
                        self.__class__)) from None
            raise ae
        if created:
            # Set timeout
            self.closure = self.timestamp + settings.TTL
            super(AJob, self).save()  # Write closure to DB
            if getattr(self, 'required_user_files', []):
                self._move_data_from_tmp_to_upload()
                super(AJob, self).save()  # Persist file changes
            # Ensure the destination folder exists (may create some issues else, depending on application usage)
            os.makedirs(os.path.join(settings.django_settings.MEDIA_ROOT, job_results(self)), exist_ok=results_exist_ok)

    def progress(self, new_state):
        """
        Signal a change in the pipeline

        Parameters
        ----------
        new_state : EStates

        Returns
        -------
        AJob.EStates
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
        state : EStates
        status : EStatuses
        started : datetime

        """
        self.started = timezone.now()
        self.progress(AJob.EStates.RUNNING)
        logger.debug("Starting {} at {}".format(self, self.started))
        return self.state, self.status, self.started

    def stop(self):
        """
        To be called when the job is completed. Can be called multiple times, will only be applied once.

        Returns
        -------
        state : EStates
        status : EStatuses
        duration : datetime.timedelta
            Duration of the job

        """
        self._set_duration()
        if self.state is not AJob.EStates.COMPLETED:
            self.status = AJob.EStatuses.FAILURE if self.has_failed() else AJob.EStatuses.SUCCESS
            self.progress(AJob.EStates.COMPLETED)  # This will also save the job
            logger.debug(
                "{} terminated in {}s with status '{}'".format(self, self.duration, self.status.label))
        return self.state, self.status, self.duration

    def failed(self, task, exception):
        """
        Mark the task as failed and stop it.

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
            dict(task=task.__name__, exception="{}".format(type(exception).__name__), msg="{}".format(exception)))
        # TODO: http://stackoverflow.com/questions/4564559/
        logger.exception("Task %s failed with following exception: %s", task.__name__, exception)
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

    upload_to_data = None

    job = None  # Just a placeholder for IDEs
    data = None  # Just a placeholder for IDEs

    if StrictVersion(django_version()) < StrictVersion('1.10.0'):
        # SEE: https://docs.djangoproject.com/en/1.10/topics/db/models/#field-name-hiding-is-not-permitted
        job = None  # Just a placeholder, Django < 1.10 does not support overriding Fields of abstract models
        data = None  # Just a placeholder, Django  < 1.10 does not support overriding Fields of abstract models
    else:
        job = models.ForeignKey(AJob, on_delete=models.CASCADE)  # placeholder, must be overridden by concrete class
        data = models.FileField(upload_to=job_data, max_length=256)
