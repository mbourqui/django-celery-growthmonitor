# -*- coding: utf-8 -*-

import os
import warnings

from django.core.files.base import ContentFile
from django.test import TestCase

from celery_growthmonitor.tests import models
from . import tasks
from .. import settings
from ..models import MetaJob, AJob
from ..workflows import chain

warnings.simplefilter("always")


class JobTestCase(TestCase):
    def setUp(self):
        self.app_root = os.path.join(settings.django_settings.MEDIA_ROOT, settings.APP_MEDIA_ROOT)

    def build_path(self, *args):
        return os.path.join(self.app_root, *args)

    def tearDown(self):
        import shutil
        # Database is not kept but files would be otherwise
        shutil.rmtree(self.build_path())

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
        expected_path = self.build_path('testjob', '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.TestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = self.build_path(models.MyRootStrTestJob.job_root, '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyRootStrTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = self.build_path('my_root_func', '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyRootFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = self.build_path('myresultsstrtestjob', '1', 'my_results_str')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyResultsStrTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = self.build_path('myresultsfunctestjob', '1', 'my_results_func', )
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyResultsFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = self.build_path('jobresultsfunctestjob', '1', 'results')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.JobResultsFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))
        #
        expected_path = self.build_path('my_root_func', '1', 'my_results_func')
        self.assertFalse(os.path.isdir(expected_path))
        test_job = models.MyRootResultsFuncTestJob()
        test_job.save()
        self.assertTrue(os.path.isdir(expected_path))

    def test_job_with_data_file(self):
        test_file = ContentFile('DUMMY CONTENT', 'foobar.txt')
        # Base case
        test_job = models.TestJob()
        test_job.save()
        test_job_two = models.TestJobTwo()
        test_job_two.save()
        expected_path = self.build_path('testjob', '1', 'data', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.TestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = self.build_path('testjobtwo', '1', 'data', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.JobDataFuncTestFile(job=test_job_two, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = self.build_path('testjob', '1', 'my_data_str', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyDataStrTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = self.build_path('testjob', '1', 'my_data_func', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyDataFuncTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        #
        test_job = models.MyRootFuncTestJob()
        test_job.save()
        expected_path = self.build_path('my_root_func', '1', 'data', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyRootFuncTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        expected_path = self.build_path('my_root_func', '1', 'my_data_func', 'foobar.txt')
        self.assertFalse(os.path.exists(expected_path))
        annotation = models.MyRootDataFuncTestFile(job=test_job, data=test_file)
        annotation.save()
        self.assertTrue(os.path.exists(expected_path))
        #
        #
        # TODO: tests with my_results_func

    def test_job_with_user_required_file(self):
        sample_file = ContentFile('SAMPLE DUMMY CONTENT', 'sample.txt')
        other_file = ContentFile('OTHER DUMMY CONTENT', 'other.txt')
        # Base case
        expected_sample_path = self.build_path('testjobwithrequiredfile', '1', 'data', 'sample.txt')
        expected_other_path = self.build_path('testjobwithrequiredfile', '1', 'data', 'other.txt')
        self.assertFalse(os.path.exists(expected_sample_path))
        self.assertFalse(os.path.exists(expected_other_path))
        test_job = models.TestJobWithRequiredFile(sample=sample_file, other=other_file)
        test_job.save()
        self.assertTrue(os.path.exists(expected_sample_path))
        self.assertTrue(os.path.exists(expected_other_path))
        # TODO: test file path in test_job


class TasksTestCase(TestCase):
    def setUp(self):
        self.job = models.TestJob()
        self.job.save()
        self.mt = MetaJob(self.job)
        self.app_root = os.path.join(settings.django_settings.MEDIA_ROOT, settings.APP_MEDIA_ROOT)

    def build_path(self, *args):
        return os.path.join(self.app_root, *args)

    def tearDown(self):
        import shutil
        # Database is not kept but files would be otherwise
        shutil.rmtree(self.build_path())

    def test_no_task(self):
        self.assertEqual(self.job.__str__(), 'TestJob 1 (Created and Active)')
        workflow = chain(self.mt, )
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertTrue(hasattr(result.result, 'metajob'))
        self.assertTrue(hasattr(result.result, 'results'))
        self.assertIsInstance(result.result.metajob, MetaJob)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result.metajob, self.mt)
        self.assertIs(result.result.results, ())
        mt = result.result.metajob
        self.assertIsNone(mt.job)
        self.assertIsNotNone(mt.get_job())
        self.assertIs(mt.job, mt._job)
        self.assertEqual(mt.job.__str__(), 'TestJob 1 (Completed and Succeeded)')

    def test_identity_task(self):
        workflow = chain(self.mt, tasks.identity_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metajob, MetaJob)
        self.assertIsInstance(result.result.results, tuple)

    def test_constant_task(self):
        workflow = chain(self.mt, tasks.constant_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metajob, MetaJob)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result[1][0], True)

    def test_parametric_task(self):
        args = (True, 2)
        workflow = chain(self.mt, tasks.parametric_task.s(*args))
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metajob, MetaJob)
        self.assertIsInstance(result.result.results, tuple)
        self.assertIs(result.result.results[0], True)
        self.assertEqual(result.result.results[1], 2)

    def test_failed_task(self):
        workflow = chain(self.mt, tasks.failing_task.s())
        result = workflow.apply_async(debug=True)
        self.assertEqual(result.state, 'SUCCESS')
        self.assertEqual(result.status, 'SUCCESS')
        self.assertIsInstance(result.result.metajob, MetaJob)
        self.assertIsInstance(result.result.results, tuple)
        mt = result.result.metajob
        job = mt.get_job()
        self.assertIs(job.state, AJob.EStates.COMPLETED)
        self.assertIs(job.status, AJob.EStatuses.FAILURE)
        self.assertTrue(job.has_failed())
        from json import loads
        error = loads(job.error)
        self.assertTrue('task' in error)
        self.assertTrue('exception' in error)
        self.assertTrue('msg' in error)
        self.assertEqual(error['exception'], RuntimeError.__name__)


class SerializationTestCase(TestCase):
    def setUp(self):
        self.job = models.TestJob()
        self.job.save()
        self.mt = MetaJob(self.job)
        self.app_root = os.path.join(settings.django_settings.MEDIA_ROOT, settings.APP_MEDIA_ROOT)

    def build_path(self, *args):
        return os.path.join(self.app_root, *args)

    def tearDown(self):
        import shutil
        # Database is not kept but files would be otherwise
        shutil.rmtree(self.build_path())

    def test_unsaved_job(self):
        job = models.TestJob()
        mt = MetaJob(job)
        self.assertRaises(job.DoesNotExist, mt.pre_serialization)

    # def test_json(self):
    #     import json
    #     json.dumps(self.mt.__dict__)
    #     self.assertIsNone(self.mt._job)
    #     self.mt.post_serialization()
    #     self.assertIsNotNone(self.mt._job)
    #     json.loads(json.dumps(self.mt.pre_serialization()))

    def test_pickle(self):
        import pickle
        self.mt.pre_serialization()
        self.assertIsNone(self.mt._job)
        self.mt.post_serialization()
        self.assertIsNotNone(self.mt._job)
        pickle.loads(pickle.dumps(self.mt.pre_serialization()))
