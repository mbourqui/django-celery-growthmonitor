from __future__ import absolute_import, unicode_literals

from celery.canvas import chain as celery_chain

from celery_growthmonitor import settings
from celery_growthmonitor.models import JobHolder
from celery_growthmonitor.tasks import remove_old_jobs, start, stop


def pre(job_holder: JobHolder, *tasks):
    flow = (start.s(job_holder),)
    if tasks:
        flow += tasks
    return flow


def post(*tasks):
    flow = ()
    if tasks:
        flow += tasks
    flow += (stop.s(),)
    if settings.TTL.seconds > 0:
        flow += (remove_old_jobs.s(),)
    return flow


def chain(job_holder: JobHolder, *tasks):
    """
    Build a chain of tasks, adding monitoring and maintenance tasks at the beginning and end of the chain

    Parameters
    ----------
    job_holder : JobHolder
    tasks : celery.shared_task

    Returns
    -------
    celery.canvas.chain

    """

    flow = pre(job_holder, *tasks) + post()
    return celery_chain(*flow)


def chain_pre(job_holder: JobHolder, *tasks):
    flow = pre(job_holder, *tasks)
    return celery_chain(*flow)


def chain_post(*tasks):
    flow = post(*tasks)
    return celery_chain(*flow)
