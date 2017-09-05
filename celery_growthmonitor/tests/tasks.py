from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ..models.metajob import MetaJob
from ..workflows.tasks import ReturnTuple


@shared_task
def identity_task(metajob: MetaJob):
    return metajob.pre_serialization()


@shared_task
def constant_task(metajob: MetaJob):
    return metajob.pre_serialization(), True


@shared_task
def parametric_task(metajob: MetaJob, *args):
    return ReturnTuple(metajob.pre_serialization(), args)
