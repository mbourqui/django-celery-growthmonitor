import logging

from celery_growthmonitor.models.job import AJob

logger = logging.getLogger(__name__)


class MetaJob:
    """
    Keep this object as simple as possible, so that it is easily serializable (pickle, json, and so on).

    Parameters
    ----------
    job : AJob
    """

    def __init__(self, job: AJob):
        self._job = job
        self._job_pk = self._job.pk
        self._job_app_label = self._job._meta.app_label
        self._job_cls = self._job.__class__.__name__

    def get_job(self):
        if not self._job:
            self.post_serialization()
        return self.job

    @property
    def job(self):
        return self._job

    def pre_serialization(self):
        if not self._job_pk:
            # The job has eventually been saved since instantiation of self
            try:
                self._job.refresh_from_db()
                self._job_pk = self._job.pk
            except self._job.DoesNotExist:
                raise self._job.DoesNotExist(
                    "{} has not yet been saved, but its primary key is required".format(self.job)) from None
        self._job = None
        return self

    def post_serialization(self):
        from django.apps import apps
        job_class = apps.get_model(self._job_app_label, self._job_cls)
        if self._job_pk is None:
            raise self._job.DoesNotExist("{} may not yet been saved, but its primary key is required. "
                                         "Did you forgot to call the {} hook before running tasks?".
                                         format(self.job, self.pre_serialization.__name__))
        self._job = job_class.objects.get(pk=self._job_pk)
        return self

    def progress(self, new_state):
        return self.job.progress(new_state)

    def start(self):
        return self.job.start()

    def stop(self):
        return self.job.stop()

    def failed(self, task, exception):
        return self.job.failed(task, exception)

    def has_failed(self):
        return self.job.has_failed()
