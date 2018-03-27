[![Python](https://img.shields.io/badge/Python-3.4,3.5,3.6-blue.svg?style=flat-square)](/)
[![Django](https://img.shields.io/badge/Django-1.8,1.9,1.10,1.11-blue.svg?style=flat-square)](/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/django_celery_growthmonitor.svg?style=flat-square)](https://pypi.org/project/django-celery-growthmonitor)
[![Build Status](https://travis-ci.org/mbourqui/django-celery-growthmonitor.svg?branch=master)](https://travis-ci.org/mbourqui/django-celery-growthmonitor)
[![Coverage Status](https://coveralls.io/repos/github/mbourqui/django-celery-growthmonitor/badge.svg?branch=master)](https://coveralls.io/github/mbourqui/django-celery-growthmonitor?branch=master)


# Django-Celery-GrowthMonitor

A Django helper to monitor jobs running Celery tasks


## Features

* Utilities to track progress of Celery tasks via in-database jobs


## Requirements

* [Python][] >= 3.4
* [Django][] >= 1.8
* [Celery][] >= 4.0.2
* [echoices][] >= 2.5.0
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
TODO

  [python]:     https://www.python.org/             "Python"
  [django]:     https://www.djangoproject.com/      "Django"
  [celery]:     http://www.celeryproject.org/       "Celery"
  [echoices]:   https://github.com/mbourqui/django-echoices         "django-echoices"
  [autoslugged]:    https://github.com/mbourqui/django-autoslugged  "django-autoslugged"