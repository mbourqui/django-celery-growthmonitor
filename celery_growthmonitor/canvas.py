from __future__ import absolute_import, unicode_literals

import sys

from celery.canvas import chain as celery_chain

from celery_growthmonitor import settings
from celery_growthmonitor.models import JobHolder
from celery_growthmonitor.tasks import remove_old_jobs, start, stop

_compat_python_lt_35 = sys.version_info < (3, 5)


def pre(job_holder: JobHolder, *tasks):
    if _compat_python_lt_35:
        flow = (start.s(job_holder),)
        if tasks:
            flow += tuple([task for task in tasks])
    else:
        flow = "(start.s(job_holder),"
        if tasks:
            flow += "*tasks,"
    return flow


def post(*tasks):
    if _compat_python_lt_35:
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

    flow = pre(job_holder, tasks) + post()
    if not _compat_python_lt_35:
        # We have to use `eval()`, because python<3.5 will not compile due to SyntaxError of the unsupported `*task`
        # notation.
        flow = eval(flow)
    return celery_chain(*flow)


def chain_pre(job_holder: JobHolder, *tasks):
    flow = pre(job_holder, tasks)
    if not _compat_python_lt_35:
        flow = eval(flow)
    return celery_chain(*flow)


def chain_post(*tasks):
    flow = post(tasks)
    if not _compat_python_lt_35:
        flow = eval(flow)
    return celery_chain(*flow)
