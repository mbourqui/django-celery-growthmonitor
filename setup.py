#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from codecs import open

from setuptools import find_packages, setup

from celery_growthmonitor import __version__, __status__

REPO_URL = "https://github.com/mbourqui/django-celery-growthmonitor/"

README = ""
for ext in ["md", "rst"]:
    try:
        with open(os.path.join(os.path.dirname(__file__), "README." + ext)) as readme:
            README = readme.read()
    except FileNotFoundError as fnfe:
        pass

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-celery-growthmonitor",
    version=__version__,
    author="Marc Bourqui",
    author_email="pypi.kemar@bourqui.org",
    license="GNU GPLv3",
    description="A Django helper to monitor jobs running Celery tasks",
    long_description=README,
    url=REPO_URL,
    download_url=REPO_URL + "releases/tag/v" + __version__,
    packages=find_packages(
        exclude=["celery_growthmonitor.tests", "celery_growthmonitor.tests.*"]
    ),
    include_package_data=True,
    package_data={"": ["*.po", "*.mo"],},
    install_requires=[
        "Django>=2.2",
        "django-echoices>=2.6.0",
        "celery>=4.0.2",
        "django-autoslug>=1.9.4",
    ],
    keywords="django utility celery celery-tasks monitoring",
    classifiers=[
        "Development Status :: " + __status__,
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Utilities",
    ],
)
