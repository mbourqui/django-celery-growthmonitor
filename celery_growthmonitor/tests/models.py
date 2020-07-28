from distutils.version import StrictVersion

from django import get_version as django_version
from django.db import models

from celery_growthmonitor.models import AJob, ADataFile, job_root, job_data, job_results


class TestJob(AJob):
    pass


class TestJobTwo(AJob):
    pass


class MyRootStrTestJob(AJob):
    root_job = "my_root_str"


def my_job_root(instance):
    import os

    return os.path.join("my_root_func", str(instance.pk))


class MyRootFuncTestJob(AJob):
    root_job = my_job_root


class MyResultsStrTestJob(AJob):
    upload_to_results = "my_results_str"


def my_job_results(instance, filename):
    import os

    return os.path.join(
        job_root(instance), "my_results_func", str(instance.pk), filename
    )


class MyResultsFuncTestJob(AJob):
    upload_to_results = my_job_results


class JobResultsFuncTestJob(AJob):
    upload_to_results = job_results


class MyRootResultsFuncTestJob(AJob):
    root_job = my_job_root
    upload_to_results = my_job_results


class ACompatDataFile(ADataFile):
    class Meta:
        abstract = True

    if StrictVersion("1.10.0") <= StrictVersion(django_version()):
        data = models.FileField(upload_to=ADataFile.upload_to_data, max_length=256)


class TestFile(ACompatDataFile):
    job = models.ForeignKey(TestJob, on_delete=models.CASCADE)
    if (
        StrictVersion("1.9.0")
        <= StrictVersion(django_version())
        < StrictVersion("1.10.0")
    ):
        data = models.FileField(upload_to=ADataFile.upload_to_data, max_length=256)


# Not supported anymore
# class MyDataStrTestFile(ACompatDataFile):
#     upload_to_data = 'my_data_str'
#     job = models.ForeignKey(TestJob, on_delete=models.CASCADE)


def my_job_data(instance, filename):
    import os

    return os.path.join(job_root(instance.job), "my_data_func", filename)


class MyDataFuncTestFile(ACompatDataFile):
    upload_to_data = my_job_data
    job = models.ForeignKey(TestJob, on_delete=models.CASCADE)
    data = models.FileField(upload_to=upload_to_data, max_length=256)


class JobDataFuncTestFile(ACompatDataFile):
    upload_to_data = job_data
    job = models.ForeignKey(TestJobTwo, on_delete=models.CASCADE)
    if (
        StrictVersion("1.9.0")
        <= StrictVersion(django_version())
        < StrictVersion("1.10.0")
    ):
        data = models.FileField(upload_to=ADataFile.upload_to_data, max_length=256)


class MyRootFuncTestFile(ACompatDataFile):
    job = models.ForeignKey(MyRootFuncTestJob, on_delete=models.CASCADE)
    if (
        StrictVersion("1.9.0")
        <= StrictVersion(django_version())
        < StrictVersion("1.10.0")
    ):
        data = models.FileField(upload_to=ADataFile.upload_to_data, max_length=256)


class MyRootDataFuncTestFile(ACompatDataFile):
    upload_to_data = my_job_data
    job = models.ForeignKey(MyRootFuncTestJob, on_delete=models.CASCADE)
    data = models.FileField(upload_to=upload_to_data, max_length=256)


class TestJobWithRequiredFile(AJob):
    sample = models.FileField(upload_to=job_data, max_length=256)
    other = models.FileField(upload_to=job_data, max_length=256)

    required_user_files = ["sample", other]
