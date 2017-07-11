from collections import namedtuple

from celery import shared_task

ReturnTuple = namedtuple('ReturnTuple', ['metatask', 'results'])


def _compat_return(metatask, *args):
    return ReturnTuple(metatask, args)


def _extract_metatask(previous_task_results, *args):
    if isinstance(previous_task_results, ReturnTuple):
        return _compat_return(previous_task_results.metatask, *(previous_task_results.results + args))
    elif isinstance(previous_task_results, tuple):
        return _compat_return(previous_task_results[0], *(previous_task_results[1:] + args))
    return previous_task_results, args


# ==================================================
#   MONITORING TASKS
# ==================================================

@shared_task
def start(metatask):
    """
    Having a task for starting the job makes sure we measure the right time of running

    Parameters
    ----------
    metatask : MetaTask

    Returns
    -------
    MetaTask
    """
    metatask.start()
    return metatask


@shared_task
def stop(metatask, *args):
    """
    Having a task for stopping the job makes sure we measure the right time of completion (previous task is obviously
    done)

    Parameters
    ----------
    metatask : MetaTask or tuple
    args

    Returns
    -------
    MetaTask

    """
    metatask, args = _extract_metatask(metatask, *args)
    metatask.stop()
    return _compat_return(metatask, *args)


# ==================================================
#   MAINTENANCE TASKS
# ==================================================

@shared_task
def remove_old_jobs(metatask, *args):
    """

    Parameters
    ----------
    metatask : MetaTask or tuple
    args

    Returns
    -------

    """
    metatask, args = _extract_metatask(metatask, *args)
    from django.utils.timezone import now
    candidates = metatask.job.__class__.objects.filter(closure__lt=now())
    for candidate in candidates:
        candidate.delete()
    return _compat_return(metatask, *args)
