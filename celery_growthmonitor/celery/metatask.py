import logging
from abc import ABCMeta
from datetime import datetime

from ..models import EStates, EStatuses

logger = logging.getLogger(__name__)


class AMetaTask:
    """
    Parameters
    ----------
    job : AJob
    """
    __metaclass__ = ABCMeta

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
