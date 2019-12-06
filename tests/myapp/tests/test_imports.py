from django.test import TestCase
from django_modeler.modeler import Modeler
from myapp.models import TestModel


class TestImports(TestCase):
    def test_simple(self):
        imp = Modeler().generate_imports(TestModel)
        self.assertIn('from myapp.models import TestModel', imp)

    def test_empty(self):
        """
        Should not cause an error
        """
        Modeler().generate_imports()
