from celery import Task


class JobFailedOnFailureTask(Task):
    """

    See Also
    --------
    https://gist.github.com/darklow/c70a8d1147f05be877c3

    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(JobFailedOnFailureTask, self).on_failure(
            exc, task_id, args, kwargs, einfo
        )
        holder = args[0]
        job = holder.get_job()
        job.failed(self, exc)
