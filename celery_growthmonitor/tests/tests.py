# -*- coding: utf-8 -*-

import warnings

from django.test import TestCase

from .models import TestJob

warnings.simplefilter("always")


class Test(TestCase):
    def test(self):
        test_job = TestJob()
