from celery.canvas import chain as celery_chain

from celery_growthmonitor.models import MetaJob
from .tasks import start, stop, remove_old_jobs


def chain(metajob, *tasks):
    """
    Build a chain of tasks, adding monitoring and maintenance tasks at the beginning and end of the chain

    Parameters
    ----------
    metajob : MetaJob
    tasks : celery.shared_task

    Returns
    -------
    celery.canvas.chain

    """
    try:
        flow = eval("""(
            start.s(metajob),
            *tasks,
            stop.s(),
            remove_old_jobs.s(),
        )""")
    except SyntaxError:
        # Python < 3.5
        flow = (start.s(metajob),)
        flow += tuple([task for task in tasks])
        flow += (
            stop.s(),
            remove_old_jobs.s(),
        )
    return celery_chain(*flow)
