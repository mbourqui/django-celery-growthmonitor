from datetime import timedelta

from django.conf import settings as django_settings

from .apps import CeleryGrowthMonitorConfig

TTL = getattr(django_settings, '{}_TTL'.format(CeleryGrowthMonitorConfig.name.upper()),
              getattr(django_settings, 'CELERY_TASK_RESULT_EXPIRES',
                      timedelta(10)))  # 10 days
"""
Time to live. After that time, jobs should be dropped from file system.
"""

APP_ROOT = getattr(django_settings, '{}_APP_ROOT'.format(CeleryGrowthMonitorConfig.name.upper()),
                   django_settings.MEDIA_ROOT)
