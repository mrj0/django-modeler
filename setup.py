#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
import os
import codecs

# A list of classifiers can be found here:
# http://pypi.python.org/pypi?%3Aaction=list_classifiers
from setuptools import find_packages

CLASSIFIERS = [
     'Development Status :: 3 - Alpha',
     'Environment :: Web Environment',
     'Framework :: Django',
     'Intended Audience :: Developers',
     'License :: OSI Approved :: zlib/libpng License',
     'Operating System :: OS Independent',
     'Programming Language :: Python',
     'Programming Language :: Python :: 2',
     'Programming Language :: Python :: 2.6',
     'Programming Language :: Python :: 2.7',
]

setup(
    author="Mike Johnson",
    author_email="mike@publicstatic.net",
    name='django-modeler',
    version="0.1",
    description='Generate django ORM code from object instances (great for testing)',
    long_description=codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8').read(),
    url='https://github.com/mrj0/django-modeler',

    license='zlib/libpng',
    platforms=['OS Independent'],

    classifiers=CLASSIFIERS,

    requires=[
        'django'
    ],
    provides=['django_modeler'],
    packages=find_packages(),
)

