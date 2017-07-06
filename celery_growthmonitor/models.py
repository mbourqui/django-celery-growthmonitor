import logging
from datetime import datetime
from enum import unique

from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from echoices.enums import EChoice
from echoices.fields import make_echoicefield

logger = logging.getLogger(__name__)


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
    import os
    return os.path.join(instance.__class__.__name__.lower(), str(instance.id))


def job_root(instance, filename):
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
    import os
    return os.path.join(root_job(instance), filename)


class AJob(models.Model):
    """
    See Also
    --------
    http://stackoverflow.com/questions/16655097/django-abstract-models-versus-regular-inheritance#16838663
    """

    class Meta:
        abstract = True

    SLUG_MAX_LENGTH = 32
    SLUG_RND_LENGTH = 6

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
    identifier = models.CharField(max_length=64, blank=True,
                                  help_text=_("Human readable identifier, as provided by the submitter"), )
    state = make_echoicefield(EStates, default=EStates.CREATED, editable=False)
    status = make_echoicefield(EStatuses, default=EStatuses.ACTIVE, editable=False)
    duration = models.DurationField(editable=False, null=True)
    slug = AutoSlugField(max_length=SLUG_MAX_LENGTH, unique=True, editable=True, populate_from=slug_default,
                         help_text=_("Human readable url, must be unique, "
                                     "a default one will be generated if none is given"))
    closure = models.DateTimeField(blank=True, null=True, help_text=_(
        "Timestamp of removal, will be set automatically on creation if not given"), )  # Default is set on save()

    def save(self, *args, **kwargs):
        created = not self.id
        super(AJob, self).save(*args, **kwargs)  # Call the "real" save() method.
        if created:
            # Set timeout
            from . import settings as app_settings
            from pytz import timezone
            self.closure = (self.timestamp + app_settings.TTL).astimezone(timezone(app_settings.settings.TIME_ZONE))


class MetaTask:
    """
    Parameters
    ----------
    job : AJob
    """

    def __init__(self, job):
        self.job = job
        self.started = None
        self.completed = None
        self.error = None

    def progress(self, new_state):
        """
        Signal a change in the pipeline

        Parameters
        ----------
        new_state : AJob.EStates

        Returns
        -------
        AJob.EStates
            The previous state

        """
        old_state = self.job.state
        self.job.state = new_state.value
        self.job.save()
        return old_state

    def start(self):
        """
        To be called when the job is to be started
        """
        self.progress(EStates.RUNNING)
        self.started = datetime.now()
        logger.debug("Starting job {} at {}".format(self.job.id, self.started))

    def stop(self):
        """
        To be called when the job is completed

        Returns
        -------
        datetime.timedelta
            Duration of the job

        """
        self.completed = datetime.now()
        self.job.status = EStatuses.FAILURE.value if self.error else EStatuses.SUCCESS.value
        self.progress(EStates.COMPLETED)  # This will also save the job
        logger.debug("Job {} terminated in {}s with status {}".format(self.job.id, self.duration,
                                                                      EStatuses.from_value(self.job.status).label))
        return self.duration

    def failed(self, exception):
        self.progress(EStates.ERROR)
        self.error = exception
        # TODO: http://stackoverflow.com/questions/4564559/
        logger.exception(exception)

    @property
    def duration(self):
        if not self.job.duration:
            self.job.duration = self.completed - self.started
            self.job.save()
        return self.job.duration
