from django.test import TestCase
from django_modeler.api import generate_imports
from tests.myapp.models import TestModel

class TestImports(TestCase):
    def test_simple(self):
        self.assertTrue('from myapp.models import TestModel' in generate_imports(TestModel))

    def test_empty(self):
        """
        Should not cause an error
        """
        generate_imports()
