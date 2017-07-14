import os

from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .. import settings


def _user_path(attribute_or_prefix, filename=''):
    if attribute_or_prefix:
        if callable(attribute_or_prefix):
            # It's an attribute
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
            return instance.job_root()
        else:
            return os.path.join(str(instance.job_root), str(instance.id))
    return os.path.join(settings.APP_ROOT, instance.__class__.__name__.lower(), str(instance.id))


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
    from enum import unique
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
        SUCCESS = (10, 'Success')
        FAILURE = (20, 'Failure')

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
            import random as rnd
            slug = slug[:self.SLUG_MAX_LENGTH - self.SLUG_RND_LENGTH] + \
                   str(rnd.randrange(10 ** (self.SLUG_RND_LENGTH - 1), 10 ** self.SLUG_RND_LENGTH))
        return slug

    timestamp = models.DateTimeField(verbose_name=_("Job creation timestamp"), auto_now_add=True)
    # TODO: validate identifier over allowance for slug or [a-zA-Z0-9_]
    identifier = models.CharField(max_length=64, blank=True, db_index=True,
                                  help_text=_("Human readable identifier, as provided by the submitter"))
    state = make_echoicefield(EStates, default=EStates.CREATED, editable=False)
    status = make_echoicefield(EStatuses, default=EStatuses.ACTIVE, editable=False)
    duration = models.DurationField(editable=False, null=True)
    slug = AutoSlugField(max_length=SLUG_MAX_LENGTH, unique=True, editable=True, populate_from=slug_default,
                         db_index=True, help_text=_("Human readable url, must be unique, "
                                                    "a default one will be generated if none is given"))
    closure = models.DateTimeField(blank=True, null=True, db_index=True, help_text=_(
        "Timestamp of removal, will be set automatically on creation if not given"))  # Default is set on save()

    def save(self, *args, **kwargs):
        created = not self.id
        super(AJob, self).save(*args, **kwargs)  # Call the "real" save() method.
        if created:
            # Set timeout
            self.closure = self.timestamp + settings.TTL
            super(AJob, self).save(*args, **kwargs)  # Write closure to DB
            # Ensure the destination folder exists (may create some issues else, depending on application usage)
            os.makedirs(os.path.join(settings.django_settings.MEDIA_ROOT, job_results(self)), exist_ok=False)


class ADataFile(models.Model):
    from django import get_version as django_version
    from distutils.version import StrictVersion

    class Meta:
        abstract = True

    upload_to_data = None

    if StrictVersion(django_version()) < StrictVersion('1.10.0'):
        # SEE: https://docs.djangoproject.com/en/1.10/topics/db/models/#field-name-hiding-is-not-permitted
        job = None  # Just a placeholder, Django < 1.10 does not support overriding Fields of abstract models
        data = None  # Just a placeholder, Django  < 1.10 does not support overriding Fields of abstract models
    else:
        job = models.ForeignKey(AJob, on_delete=models.CASCADE)  # placeholder, must be overridden by concrete class
        data = models.FileField(upload_to=job_data, max_length=256)
