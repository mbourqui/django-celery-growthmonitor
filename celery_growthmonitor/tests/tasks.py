from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ..models.metajob import MetaJob
from ..workflows.tasks import ReturnTuple


@shared_task
def identity_task(metajob: MetaJob):
    metajob.post_serialization()
    return metajob.pre_serialization()


@shared_task
def constant_task(metajob: MetaJob):
    metajob.post_serialization()
    return metajob.pre_serialization(), True


@shared_task
def parametric_task(metajob: MetaJob, *args):
    metajob.post_serialization()
    return ReturnTuple(metajob.pre_serialization(), args)


@shared_task
def failing_task(metajob: MetaJob):
    metajob.post_serialization()
    metajob.failed(failing_task, RuntimeError("Please do not disturb this task"))
    return metajob.pre_serialization()
