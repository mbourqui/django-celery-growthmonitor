import logging
from datetime import datetime

from celery_growthmonitor.models.job import AJob
try:
    from types import SimpleNamespace
except ImportError:
    # SEE: https://docs.python.org/3/library/types.html#types.SimpleNamespace
    class SimpleNamespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

logger = logging.getLogger(__name__)


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
        new_state : EStates

        Returns
        -------
        AJob.EStates
            The previous state

        """
        old_state = self.job.state
        self.job.state = new_state
        self.job.save()
        return old_state

    def start(self):
        """
        To be called when the job is to be started
        """
        self.progress(AJob.EStates.RUNNING)
        self.started = datetime.now()
        logger.debug("Starting {} at {}".format(self.job, self.started))

    def stop(self):
        """
        To be called when the job is completed

        Returns
        -------
        datetime.timedelta
            Duration of the job

        """
        self.completed = datetime.now()
        self.job.status = AJob.EStatuses.FAILURE if self.has_failed() else AJob.EStatuses.SUCCESS
        self.progress(AJob.EStates.COMPLETED)  # This will also save the job
        logger.debug(
            "{} terminated in {}s with status '{}'".format(self.job, self.duration, self.job.status.label))
        return self.duration

    def failed(self, task, exception):
        self.error = SimpleNamespace(task=task.__name__, exception=exception)
        # TODO: http://stackoverflow.com/questions/4564559/
        logger.exception("Task %s failed with following exception: %s", task.__name__, exception)

    def has_failed(self):
        return bool(self.error)

    @property
    def duration(self):
        if not self.job.duration:
            self.job.duration = self.completed - self.started
            self.job.save()
        return self.job.duration
