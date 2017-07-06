from datetime import timedelta

from django.conf import settings

from .apps import CeleryGrowthMonitorConfig

TTL = getattr(settings, '{}_TTL'.format(CeleryGrowthMonitorConfig.name.upper()),
              getattr(settings, 'CELERY_TASK_RESULT_EXPIRES',
                      timedelta(10)))  # 10 days
"""
Time to live. After that time, jobs should be dropped from file system.
"""
