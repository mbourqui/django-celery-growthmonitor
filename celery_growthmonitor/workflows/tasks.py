from celery import shared_task


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
    from django.utils.timezone import now
    candidates = metatask.job.__class__.objects.filter(closure__lt=now())
    for candidate in candidates:
        candidate.delete()
    # TODO: return args (and kwargs) if any
    return metatask
