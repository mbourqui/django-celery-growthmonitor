from __future__ import absolute_import

import os
from distutils.version import StrictVersion

import django

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DEBUG = False

SECRET_KEY = 'm+qa*7_8t-=17zt_)9gi)4g%6w*v$xxkh6rwrys*bn9su+5%du'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'celery_growthmonitor',

    'celery_growthmonitor.tests',
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
]

if StrictVersion(django.get_version()) < StrictVersion('1.10.0'):
    MIDDLEWARE_CLASSES = MIDDLEWARE

TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'en'

SITE_ID = 1

USE_I18N = True

USE_TZ = True

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/stable/ref/settings/#media-root
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# See: https://docs.djangoproject.com/en/stable/ref/settings/#media-url
MEDIA_URL = '/media/'

# CELERY
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['celery_growthmonitor.tests.taskapp.celery.CeleryConfig', ]
CELERY_ALWAYS_EAGER = True
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'

# CELERY-GROWTHMONITOR
# ------------------------------------------------------------------------------
CELERY_GROWTHMONITOR_APP_ROOT = os.path.join(MEDIA_ROOT, 'c_gm')
