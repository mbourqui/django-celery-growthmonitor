from celery import shared_task
from celery.canvas import chain

from celery_growthmonitor.models import MetaTask


def build_chain(metatask, *tasks):
    """
    Build a chain of tasks, adding monitoring and maintenance tasks at the beginning and end of the chain

    Parameters
    ----------
    metatask : MetaTask
    tasks : genrepa.celery.metatask.AMetaTask

    Returns
    -------
    celery.canvas.chain

    """
    try:
        chain_ = eval("""(
            start.s(metatask),
            *tasks,
            stop.s(),
            remove_old_jobs.s(),
        )""")
    except SyntaxError:
        # Python < 3.5
        chain_ = (
            start.s(metatask),)
        chain_ += tuple([task for task in tasks])
        chain_ += (
            stop.s(),
            remove_old_jobs.s(),
        )
    return chain(*chain_)


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
def stop(metatask):
    """
    Having a task for stopping the job makes sure we measure the right time of completion

    Parameters
    ----------
    metatask : MetaTask

    Returns
    -------
    MetaTask

    """
    metatask.stop()
    # TODO: return args (and kwargs) if any
    return metatask


# ==================================================
#   MAINTENANCE TASKS
# ==================================================

@shared_task
def remove_old_jobs(metatask):
    from datetime import datetime
    candidates = metatask.job.__class__.objects.filter(closure__lt=datetime.now())
    for candidate in candidates:
        candidate.delete()
    # TODO: return args (and kwargs) if any
    return metatask
