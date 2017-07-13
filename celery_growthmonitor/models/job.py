import os

from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .. import settings


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


def job_data(instance, filename):
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
    return os.path.join(job_root(instance.job) if isinstance(instance, ADataFile) else root_job(instance),
                        'data', filename)


def job_results(instance, filename):
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
    return os.path.join(job_root(instance), 'results', filename)


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

    upload_to_results = job_results

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
            from .. import settings as app_settings
            self.closure = self.timestamp + app_settings.TTL
            super(AJob, self).save(*args, **kwargs)  # Write closure to DB
            # Ensure the destination folder exists (may create some issues else, depending on application usage)
            os.makedirs(self.upload_to_results(''), exist_ok=False)


class ADataFile(models.Model):
    class Meta:
        abstract = True

    upload_to_data = job_data

    job = models.ForeignKey(AJob, on_delete=models.CASCADE)
    data = models.FileField(upload_to=upload_to_data)
