from __future__ import absolute_import, unicode_literals

from collections import namedtuple

from celery import shared_task

from .models.jobholder import JobHolder

ReturnTuple = namedtuple("ReturnTuple", ["job_holder", "results"])


def _compat_return(job_holder: JobHolder, *args):
    return ReturnTuple(job_holder, args)


def extract_job_holder(previous_task_results, *args):
    """

    Parameters
    ----------
    previous_task_results
    args

    Returns
    -------
    ReturnTuple
        job_holder : JobHolder
            post_serialization() has already been called
        results : tuple

    """
    if isinstance(previous_task_results, ReturnTuple):
        return _compat_return(
            previous_task_results.job_holder.post_serialization(),
            *(previous_task_results.results + args)
        )
    elif isinstance(previous_task_results, tuple):
        return _compat_return(
            previous_task_results[0].post_serialization(),
            *(previous_task_results[1:] + args)
        )
    return _compat_return(previous_task_results.post_serialization(), *args)


# ==================================================
#   MONITORING TASKS
# ==================================================


@shared_task
def start(job_holder):
    """
    Having a task for starting the job makes sure we measure the right time of running

    Parameters
    ----------
    job_holder : JobHolder

    Returns
    -------
    JobHolder

    """
    job_holder.post_serialization()
    job_holder.job.start()
    return job_holder.pre_serialization()


@shared_task
def stop(job_holder, *args):
    """
    Having a task for stopping the job makes sure we measure the right time of completion (previous task is obviously
    done)

    Parameters
    ----------
    job_holder : JobHolder or tuple
    args

    Returns
    -------
    JobHolder

    """
    job_holder, args = extract_job_holder(job_holder, *args)
    job_holder.job.stop()
    return _compat_return(job_holder.pre_serialization(), *args)


# ==================================================
#   MAINTENANCE TASKS
# ==================================================


@shared_task
def remove_old_jobs(job_holder, *args):
    """

    Parameters
    ----------
    job_holder : JobHolder or tuple
    args

    Returns
    -------

    """
    job_holder, args = extract_job_holder(job_holder, *args)
    from django.utils.timezone import now

    candidates = job_holder.job.__class__.objects.filter(closure__lt=now())
    for candidate in candidates:
        candidate.delete()
    return _compat_return(job_holder.pre_serialization(), *args)
