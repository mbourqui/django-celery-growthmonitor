from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ..models.jobholder import JobHolder
from ..tasks import ReturnTuple


@shared_task
def identity_task(job_holder: JobHolder):
    job_holder.post_serialization()
    return job_holder.pre_serialization()


@shared_task
def constant_task(job_holder: JobHolder):
    job_holder.post_serialization()
    return job_holder.pre_serialization(), True


@shared_task
def parametric_task(job_holer: JobHolder, *args):
    job_holer.post_serialization()
    return ReturnTuple(job_holer.pre_serialization(), args)


@shared_task
def failing_task(job_holder: JobHolder):
    job_holder.post_serialization()
    job_holder.job.failed(failing_task, RuntimeError("Please do not disturb this task"))
    return job_holder.pre_serialization()
