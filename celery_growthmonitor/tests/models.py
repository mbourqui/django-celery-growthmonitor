from django.db import models

from celery_growthmonitor.models import AJob, ADataFile


class TestJob(AJob):
    pass


class MyRootStrTestJob(AJob):
    job_root = 'my_root_str'


def my_job_root(instance):
    import os
    return os.path.join('my_root_func', str(instance.pk))


class MyRootFuncTestJob(AJob):
    job_root = my_job_root


class MyResultsStrTestJob(AJob):
    upload_to_results = 'my_results_str'


def my_job_results(instance, filename):
    import os
    return os.path.join('my_results_func', str(instance.pk), filename)


class MyResultsFuncTestJob(AJob):
    upload_to_results = my_job_results


class MyRootResultsFuncTestJob(AJob):
    job_root = my_job_root
    upload_to_results = my_job_results


class TestFile(ADataFile):
    job = models.ForeignKey(TestJob, on_delete=models.CASCADE)


class MyDataStrTestFile(ADataFile):
    upload_to_data = 'my_data_str'
    job = models.ForeignKey(TestJob, on_delete=models.CASCADE)


def my_job_data(instance, filename):
    import os
    return os.path.join('my_data_func', filename)


class MyDataFuncTestFile(ADataFile):
    upload_to_data = my_job_data
    job = models.ForeignKey(TestJob, on_delete=models.CASCADE)


class MyRootFuncTestFile(ADataFile):
    job = models.ForeignKey(MyRootFuncTestJob, on_delete=models.CASCADE)


class MyRootDataFuncTestFile(ADataFile):
    upload_to_data = my_job_data
    job = models.ForeignKey(MyRootFuncTestJob, on_delete=models.CASCADE)
