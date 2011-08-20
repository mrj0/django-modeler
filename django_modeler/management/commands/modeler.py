from __future__ import print_function
from optparse import make_option

from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model, DateField, DateTimeField, ForeignKey
from django.db.models.fields.related import OneToOneField
from django.utils.datastructures import SortedDict

from django_modeler.api import generate_imports, get_object_dependencies, generate_orm, generate

class Command(BaseCommand):
    args = '<model [filter option] [filter option] ...>'
    help = 'Writes data to ORM code to the console'
    indent = 4

    option_list = BaseCommand.option_list + (
        make_option('-f', '--filter',
            action='append',
            dest='filter',
            type='string',
            help='Filter objects'),
        make_option('-e', '--exclude',
            action='append',
            dest='exclude',
            type='string',
            help='Exclude objects'),
        make_option('-r', '--related',
            action='store',
            dest='related',
            type='int',
            default=0,
            help='number of object relationship levels to pull (does not resolve circular references).'),
        )

    def parse_args(self, *args, **options):
        name = args[0]
        model_class = get_model(*name.split('.'))
        if not model_class:
            raise CommandError, 'Error: model not found: {0}'.format(name)

        filters = {}
        for arg in options.get('filter') or []:
            if '=' not in arg:
                raise CommandError, 'Filter syntax is name=value. Invalid argument {0}'.format(arg)
            filters.__setitem__(*arg.split('=', 1))
        excludes = {}
        for arg in options.get('exclude') or []:
            if '=' not in arg:
                raise CommandError, 'Exclude syntax is name=value. Invalid argument {0}'.format(arg)
            excludes.__setitem__(*arg.split('=', 1))
        self.query_related = options['related']

        qs = model_class.objects.all().filter(**filters)
        qs = qs.exclude(**excludes)
        return qs

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError, 'Error: modeler only accepts one model argument'

        # get a list of objects to start from
        roots = self.parse_args(*args, **options)
        print(generate(*roots, query_related=self.query_related))
