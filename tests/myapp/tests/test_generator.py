from __future__ import absolute_import
from django.test import TestCase
from myapp.tests import data
from django.contrib.auth.models import User
from django_modeler.api import Modeler
from tests.myapp.models import TestModel

class TestGenerator(TestCase):
    def setUp(self):
        data.load()

    def test_simple(self):
        code = Modeler(query_related=0).generate(TestModel.objects.get(pk=1))
        self.assertTrue('testmodel1' in code)
        self.assertTrue('relatedtotestmodel' not in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_related(self):
        code = Modeler(query_related=2).generate(User.objects.get(pk=1))
        self.assertTrue('testmodel1' in code)
        self.assertTrue('relatedtotestmodel' in code)
        self.assertTrue('user=user1' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_exclude_related_app(self):
        code = Modeler(query_related=2, exclude_related=['myapp']).generate(User.objects.get(pk=1))
        self.assertFalse('testmodel1' in code)
        self.assertFalse('relatedtotestmodel' in code)
        self.assertFalse('user=user1' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_exclude_related_model(self):
        code = Modeler(query_related=2, exclude_related=['myapp.relatedtotestmodel']).generate(User.objects.get(pk=1))
        self.assertTrue('testmodel1' in code)
        self.assertTrue('user=user1' in code)
        self.assertFalse('relatedtotestmodel' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_exclude_fields(self):
        code = Modeler(query_related=0, exclude_fields=['auth']).generate(TestModel.objects.get(pk=1))
        self.assertFalse('user' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_exclude_field_model(self):
        code = Modeler(query_related=0, exclude_fields=['auth.user']).generate(TestModel.objects.get(pk=1))
        self.assertFalse('user' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_none(self):
        '''regression'''
        code = Modeler(query_related=2).generate(TestModel.objects.get(pk=2))
        self.assertTrue('testmodel2' in code)
        exec(code)
        TestModel.objects.get(pk=2)
