# -*- coding: utf-8 -*-

import os
import warnings

from django.core.files.base import ContentFile
from django.test import TestCase

from celery_growthmonitor.tests import models
from . import tasks
from .. import settings
from ..models import MetaTask
from ..workflows import chain

warnings.simplefilter("always")


class JobTestCase(TestCase):
    def tearDown(self):
        import os
        import shutil
        # Database is not kept but files would be otherwise
        shutil.rmtree(os.path.join(settings.django_settings.MEDIA_ROOT, ))

    def test_timezone(self):
        from django.conf import settings
        for switch in [False, True]:
            settings.USE_TZ = switch
            test_job = models.TestJob()
            self.assertRaisesMessage(AssertionError, 'RuntimeWarning not triggered by save', self.assertWarnsRegex,
                                     RuntimeWarning, 'DateTimeField TestJob.closure received a naive datetime',
                                     test_job.save)

    def test_job(self):
        # Base case
        expected_path = os.path.join(settings.APP_ROOT, 'testjob', '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.TestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = os.path.join(settings.django_settings.MEDIA_ROOT, models.MyRootStrTestJob.job_root,
                                     '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyRootStrTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = os.path.join(settings.django_settings.MEDIA_ROOT, 'my_root_func', '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyRootFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = os.path.join(settings.APP_ROOT, 'myresultsstrtestjob', '1', 'my_results_str')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyResultsStrTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = os.path.join(settings.APP_ROOT, 'myresultsfunctestjob', '1', 'my_results_func')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyResultsFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = os.path.join(settings.APP_ROOT, 'jobresultsfunctestjob', '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.JobResultsFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = os.path.join(settings.django_settings.MEDIA_ROOT, 'my_root_func', '1', 'my_results_func')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyRootResultsFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))

    def test_job_with_file(self):
        test_file = ContentFile('DUMMY CONTENT', 'foobar.txt')
        # Base case
        test_job = models.TestJob()
        test_job.save()
        test_job_two = models.TestJobTwo()
        test_job_two.save()
        expected_path = os.path.join(settings.APP_ROOT, 'testjob', '1', 'data', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.TestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = os.path.join(settings.APP_ROOT, 'testjobtwo', '1', 'data', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.JobDataFuncTestFile(job=test_job_two, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = os.path.join(settings.APP_ROOT, 'testjob', '1', 'my_data_str', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyDataStrTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = os.path.join(settings.APP_ROOT, 'testjob', '1', 'my_data_func', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyDataFuncTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        #
        test_job = models.MyRootFuncTestJob()
        test_job.save()
        expected_path = os.path.join(settings.django_settings.MEDIA_ROOT, 'my_root_func', '1', 'data', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyRootFuncTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = os.path.join(settings.django_settings.MEDIA_ROOT, 'my_root_func', '1', 'my_data_func',
                                     'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyRootDataFuncTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))


class TasksTestCase(TestCase):
    def setUp(self):
        self.job = models.TestJob()
        self.job.save()
        self.mt = MetaTask(self.job)

    def tearDown(self):
        from django.conf import settings
        import os
        import shutil
        # Database is not kept but files would be otherwise
        shutil.rmtree(os.path.join(settings.CELERY_GROWTHMONITOR_APP_ROOT, ))

    def test_no_task(self):
        self.assertEqual(self.job.__str__(), 'TestJob 1 (Created and Active)')
        workflow = chain(self.mt, )
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result[0], MetaTask)
        self.assertIsInstance(result.result[1], tuple)
        self.assertEqual(self.job.__str__(), 'TestJob 1 (Completed and Succeeded)')

    def test_identity_task(self):
        workflow = chain(self.mt, tasks.identity_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metatask, MetaTask)
        self.assertIsInstance(result.result.results, tuple)

    def test_constant_task(self):
        workflow = chain(self.mt, tasks.constant_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metatask, MetaTask)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result[1][0], True)

    def test_parametric_task(self):
        args = (True, 2)
        workflow = chain(self.mt, tasks.parametric_task.s(*args))
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metatask, MetaTask)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result.results[0], True)
        self.assertEqual(result.result.results[1], 2)
