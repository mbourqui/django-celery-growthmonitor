# -*- coding: utf-8 -*-

import warnings

from django.test import TestCase

from celery_growthmonitor.models import MetaTask
from celery_growthmonitor.tests.models import TestJob
from celery_growthmonitor.tests.tasks import identity_task, constant_task, parametric_task
from celery_growthmonitor.workflows import chain

warnings.simplefilter("always")


class Test(TestCase):
    def tearDown(self):
        from django.conf import settings
        import os
        import shutil
        # Database is not kept but files would be otherwise
        shutil.rmtree(os.path.join(settings.CELERY_GROWTHMONITOR_APP_ROOT, ))

    def test_no_task(self):
        test_job = TestJob()
        test_job.save()
        mt = MetaTask(test_job)
        workflow = chain(mt, )
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result[0], MetaTask)
        self.assertIsInstance(result.result[1], tuple)

    def test_identity_task(self):
        test_job = TestJob()
        test_job.save()
        mt = MetaTask(test_job)
        workflow = chain(mt, identity_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metatask, MetaTask)
        self.assertIsInstance(result.result.results, tuple)

    def test_constant_task(self):
        test_job = TestJob()
        test_job.save()
        mt = MetaTask(test_job)
        workflow = chain(mt, constant_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metatask, MetaTask)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result[1][0], True)

    def test_parametric_task(self):
        test_job = TestJob()
        test_job.save()
        mt = MetaTask(test_job)
        args = (True, 2)
        workflow = chain(mt, parametric_task.s(*args))
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metatask, MetaTask)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result.results[0], True)
        self.assertEqual(result.result.results[1], 2)

    def test_timezone(self):
        from django.conf import settings
        for switch in [False, True]:
            settings.USE_TZ = switch
            test_job = TestJob()
            self.assertRaisesMessage(AssertionError, 'RuntimeWarning not triggered by save', self.assertWarnsRegex,
                                     RuntimeWarning, 'DateTimeField TestJob.closure received a naive datetime',
                                     test_job.save)
