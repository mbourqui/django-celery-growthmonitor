# -*- coding: utf-8 -*-

import warnings

from django.test import TestCase

from celery_growthmonitor.canvas import build_chain
from celery_growthmonitor.models import MetaTask
from celery_growthmonitor.tests.models import TestJob
from celery_growthmonitor.tests.tasks import identity_task

warnings.simplefilter("always")


class Test(TestCase):
    def test_no_task(self):
        test_job = TestJob()
        test_job.save()
        mt = MetaTask(test_job)
        task = build_chain(mt,)
        result = task.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result, MetaTask)

    def test_identity_task(self):
        test_job = TestJob()
        test_job.save()
        mt = MetaTask(test_job)
        task = build_chain(mt, identity_task.s())
        result = task.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result, MetaTask)
