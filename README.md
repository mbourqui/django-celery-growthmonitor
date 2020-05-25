[![Python](https://img.shields.io/badge/Python-3.5,3.6,3.7,3.8-blue.svg?style=flat-square)](/)
[![Django](https://img.shields.io/badge/Django-1.11,2.1,2.2-blue.svg?style=flat-square)](/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/django_celery_growthmonitor.svg?style=flat-square)](https://pypi.org/project/django-celery-growthmonitor)
[![Build Status](https://travis-ci.org/mbourqui/django-celery-growthmonitor.svg?branch=master)](https://travis-ci.org/mbourqui/django-celery-growthmonitor)
[![Coverage Status](https://coveralls.io/repos/github/mbourqui/django-celery-growthmonitor/badge.svg?branch=master)](https://coveralls.io/github/mbourqui/django-celery-growthmonitor?branch=master)
[![Downloads](https://pepy.tech/badge/django-celery-growthmonitor)](https://pepy.tech/project/django-celery-growthmonitor)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>


# Django-Celery-GrowthMonitor

A Django helper to monitor jobs running Celery tasks


## Features

* Utilities to track progress of Celery tasks via in-database jobs


## Requirements

* [Python][] >= 3.5
* [Django][] >= 1.11
* [Celery][] >= 4.0.2
* [echoices][] >= 2.6.0
* [autoslugged][] >= 2.0.0


## Installation

### Using PyPI
1. Run `pip install django-celery-growthmonitor`

### Using the source code
1. Make sure [`pandoc`](http://pandoc.org/index.html) is installed
1. Run `./pypi_packager.sh`
1. Run `pip install dist/django_celery_growthmonitor-x.y.z-[...].wheel`, where `x.y.z` must be replaced by the actual
   version number and `[...]` depends on your packaging configuration


## Usage

```Django
('state', echoices.fields.make_echoicefield(default=celery_growthmonitor.models.AJob.EState.CREATED, echoices=celery_growthmonitor.models.AJob.EState, editable=False)),
('status', echoices.fields.make_echoicefield(default=celery_growthmonitor.models.AJob.EStatus.ACTIVE, echoices=celery_growthmonitor.models.AJob.EStatus, editable=False)),
```

```Django
from .celery import app

@app.task
def my_task(holder: JobHolder, *args):
    job = holder.get_job()
    # Some processing
    job.save()
    return holder.pre_serialization()
```

### Helpers

Automatically set the job failed on task failure using custom base Task class
```Django
from celery_growthmonitor.models.task import JobFailedOnFailureTask

@app.task(base=JobFailedOnFailureTask, bind=True)
def my_task(self, holder: JobHolder):
    pass
```

#### Admin

```Django
from django.contrib import admin

from celery_growthmonitor.admin import AJobAdmin

@admin.register(MyJob)
class MyJobAdmin(AJobAdmin):
    fields = AJobAdmin.fields + ('my_extra_field',)
    readonly_fields = AJobAdmin.readonly_fields + ('my_extra_field',)

```


  [python]:     https://www.python.org/             "Python"
  [django]:     https://www.djangoproject.com/      "Django"
  [celery]:     http://www.celeryproject.org/       "Celery"
  [echoices]:   https://github.com/mbourqui/django-echoices         "django-echoices"
  [autoslugged]:    https://github.com/mbourqui/django-autoslugged  "django-autoslugged"