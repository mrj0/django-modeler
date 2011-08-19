import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from django.core.management import setup_environ
import settings as settings
setup_environ(settings)

import unittest

from django_modeler.api import generate_imports
from tests.myapp.models import TestModel

class TestImports(unittest.TestCase):
    def test_simple(self):
        self.assertTrue('from myapp.models import TestModel' in generate_imports(TestModel))

    def test_empty(self):
        """
        Should not cause an error
        """
        generate_imports()

if __name__ == '__main__':
    unittest.main()
