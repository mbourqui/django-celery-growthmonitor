from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ..workflows.tasks import _compat_return


@shared_task
def identity_task(metajob):
    return metajob


@shared_task
def constant_task(metajob):
    return metajob, True


@shared_task
def parametric_task(metajob, *args):
    return _compat_return(metajob, *args)
