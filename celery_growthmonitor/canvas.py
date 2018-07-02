from __future__ import absolute_import, unicode_literals

import sys

from celery.canvas import chain as celery_chain

from celery_growthmonitor import settings
from celery_growthmonitor.models import JobHolder
from celery_growthmonitor.tasks import remove_old_jobs, start, stop


def pre(job_holder: JobHolder, *tasks):
    if sys.version_info < (3, 5):
        flow = (start.s(job_holder),)
        if tasks:
            flow += tuple([task for task in tasks])
    else:
        flow = "(start.s(job_holder),"
        if tasks:
            flow += "*tasks,"
    return flow


def post(*tasks):
    if sys.version_info < (3, 5):
        flow = ()
        if tasks:
            flow += tuple([task for task in tasks])
        flow += (stop.s(),)
        if settings.TTL.seconds > 0:
            flow += (remove_old_jobs.s(),)
    else:
        flow = ""
        if tasks:
            flow += "*tasks,"
        flow += "stop.s()"
        if settings.TTL.seconds > 0:
            flow += ",remove_old_jobs.s()"
        flow += ")"
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
    try:
        flow = eval(pre(job_holder, tasks) + post())
    except SyntaxError:
        # Python < 3.5
        flow = pre(job_holder, tasks)
        flow += post()
    return celery_chain(*flow)


def chain_pre(job_holder: JobHolder, *tasks):
    try:
        flow = eval(pre(job_holder, tasks))
    except SyntaxError:
        # Python < 3.5
        flow = pre(job_holder, tasks)
    return celery_chain(*flow)


def chain_post(*tasks):
    try:
        flow = eval(post(tasks))
    except SyntaxError:
        # Python < 3.5
        flow = post(tasks)
    return celery_chain(*flow)
