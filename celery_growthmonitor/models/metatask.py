import logging
from datetime import datetime

from celery_growthmonitor.models.job import AJob

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
        self.job.status = AJob.EStatuses.FAILURE if self.error else AJob.EStatuses.SUCCESS
        self.progress(AJob.EStates.COMPLETED)  # This will also save the job
        logger.debug(
            "Job {} terminated in {}s with status {}".format(self.job.id, self.duration, self.job.status.label))
        return self.duration

    def failed(self, exception):
        self.progress(AJob.EStates.ERROR)
        self.error = exception
        # TODO: http://stackoverflow.com/questions/4564559/
        logger.exception(exception)

    @property
    def duration(self):
        if not self.job.duration:
            self.job.duration = self.completed - self.started
            self.job.save()
        return self.job.duration
