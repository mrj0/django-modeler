import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
print sys.path

from django.core.management import setup_environ
import settings as settings
setup_environ(settings)

import unittest

from django_modeler.api.generator import generate_imports
from tests.myapp.models import TestModel

class TestImports(unittest.TestCase):
    def test_simple(self):
        self.assertEqual('from myapp.models import TestModel', generate_imports(TestModel)[0])

if __name__ == '__main__':
    unittest.main()
