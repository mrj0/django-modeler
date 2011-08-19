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
        code = api.generate(TestModel.objects.get(pk=1), query_related=1)
        self.assertTrue('testmodel1' in code)
        self.assertTrue('relatedtotestmodel' in code)
        print code
        exec(code)
        TestModel.objects.get(pk=1)
        