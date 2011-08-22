from django.test import TestCase
from myapp.tests import data
from django_modeler import api
from django.contrib.auth.models import User
from tests.myapp.models import TestModel

class TestGenerator(TestCase):
    def setUp(self):
        data.load()

    def test_simple(self):
        code = api.generate(TestModel.objects.get(pk=1), query_related=0)
        self.assertTrue('testmodel1' in code)
        self.assertTrue('relatedtotestmodel' not in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_related(self):
        code = api.generate(User.objects.get(pk=1), query_related=2)
        self.assertTrue('testmodel1' in code)
        self.assertTrue('relatedtotestmodel' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_exclude_related_app(self):
        code = api.generate(User.objects.get(pk=1), query_related=2, exclude_related_apps=['myapp'])
        self.assertFalse('testmodel1' in code)
        self.assertFalse('relatedtotestmodel' in code)
        exec(code)
        TestModel.objects.get(pk=1)

    def test_exclude_related_model(self):
        code = api.generate(User.objects.get(pk=1), query_related=2, exclude_related_models=['myapp.relatedtotestmodel'])
        self.assertTrue('testmodel1' in code)
        self.assertFalse('relatedtotestmodel' in code)
        exec(code)
        TestModel.objects.get(pk=1)
    