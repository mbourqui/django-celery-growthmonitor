from __future__ import absolute_import

import os

from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celery_growthmonitor.tests.settings')  # pragma: no cover

app = Celery('celery_growthmonitor.tests')


class CeleryConfig(AppConfig):
    name = 'celery_growthmonitor.tests.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object('django.conf:settings')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover
