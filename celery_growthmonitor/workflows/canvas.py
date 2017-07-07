from celery.canvas import chain as celery_chain

from celery_growthmonitor.models import MetaTask
from .tasks import start, stop, remove_old_jobs


def chain(metatask, *tasks):
    """
    Build a chain of tasks, adding monitoring and maintenance tasks at the beginning and end of the chain

    Parameters
    ----------
    metatask : MetaTask
    tasks : celery.shared_task

    Returns
    -------
    celery.canvas.chain

    """
    try:
        flow = eval("""(
            start.s(metatask),
            *tasks,
            stop.s(),
            remove_old_jobs.s(),
        )""")
    except SyntaxError:
        # Python < 3.5
        flow = (start.s(metatask),)
        flow += tuple([task for task in tasks])
        flow += (
            stop.s(),
            remove_old_jobs.s(),
        )
    return celery_chain(*flow)
