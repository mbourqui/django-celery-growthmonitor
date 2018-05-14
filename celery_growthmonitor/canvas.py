from celery.canvas import chain as celery_chain

from celery_growthmonitor.models import JobHolder
from .tasks import start, stop, remove_old_jobs

from . import settings


def chain(job_holder, *tasks):
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
        flow = eval("""(
            start.s(job_holder),
            *tasks,
            stop.s(),
            remove_old_jobs.s(),
        )""")
    except SyntaxError:
        # Python < 3.5
        flow = (start.s(job_holder),)
        flow += tuple([task for task in tasks])
        flow += (stop.s(),)
        if settings.TTL.seconds > 0:
            flow += (remove_old_jobs.s(),),
    return celery_chain(*flow)
