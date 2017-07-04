from enum import unique

from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from echoices.enums import EChoice
from echoices.fields import make_echoicefield


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
    Returns the path for the pep_class_map file. The files are stored in directories linked
    to jobs.

    Parameters
    ----------
    instance
        The model instance associated with the file
    filename : str
        Original filename

    Returns
    --------
    str
        New filename which is unique for a job
    """
    import os
    return os.path.join(instance.__class__.__name__.lower(), str(instance.id))


def job_root(instance, filename):
    """
    Returns the path for the pep_class_map file. The files are stored in directories linked
    to jobs.

    Parameters
    ----------
    instance
        The model instance associated with the file
    filename : str
        Original filename

    Returns
    --------
    str
        New filename which is unique for a job
    """
    import os
    return os.path.join(root_job(instance), filename)


def ttl_default():
    # Set timeout
    from datetime import datetime
    from pytz import timezone
    from . import settings as app_settings
    return (datetime.now() + app_settings.TTL).astimezone(timezone(app_settings.settings.TIME_ZONE))


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
    closure = models.DateTimeField(blank=True, null=True, default=ttl_default, help_text=_(
        "Timestamp of removal, will be set automatically on creation if not given"), )

    def save(self, *args, **kwargs):
        created = not self.id
        super().save(*args, **kwargs)  # Call the "real" save() method.
        if created:
            # Set timeout
            from . import settings as app_settings
            from pytz import timezone
            self.closure = (self.timestamp + app_settings.TTL).astimezone(timezone(app_settings.settings.TIME_ZONE))
