#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from codecs import open

from setuptools import find_packages, setup

from celery_growthmonitor import __version__

REPO_URL = "https://github.com/mbourqui/django-celery-growthmonitor/"

with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-celery-growthmonitor',
    version=__version__,
    author='Marc Bourqui',
    author_email='pypi.kemar@bourqui.org',
    license='GNU GPLv3',
    description='A Django helper to monitor jobs running Celery tasks',
    long_description=README,
    url=REPO_URL,
    download_url=REPO_URL + 'releases/tag/v' + __version__,
    packages=find_packages(exclude=['celery_growthmonitor.tests', 'celery_growthmonitor.tests.*']),
    include_package_data=True,
    package_data={
        '': ['*.po', '*.mo'],
    },
    install_requires=[
        'Django>=1.9.13',
        'django-echoices>=2.5.0',
        'celery>=4.0.2',
        'django-autoslug>=1.9.3',
    ],
    keywords='django utility celery celery-tasks',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Utilities',
    ],
)
