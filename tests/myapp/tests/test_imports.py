from __future__ import absolute_import
from django.test import TestCase
from django_modeler.api import Modeler
from tests.myapp.models import TestModel

class TestImports(TestCase):
    def test_simple(self):
        self.assertTrue('from myapp.models import TestModel' in Modeler().generate_imports(TestModel))

    def test_empty(self):
        """
        Should not cause an error
        """
        Modeler().generate_imports()
