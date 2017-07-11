from __future__ import absolute_import, unicode_literals
from ..workflows.tasks import _compat_return
from celery import shared_task


@shared_task
def identity_task(metatask):
    return metatask


@shared_task
def constant_task(metatask):
    return metatask, True


@shared_task
def parametric_task(metatask, *args):
    return _compat_return(metatask, *args)
