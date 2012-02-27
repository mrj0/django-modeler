from __future__ import print_function
from __future__ import absolute_import
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model
import sys

from django_modeler.modeler import Modeler

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
        make_option('--exclude-related',
            action='append',
            dest='exclude_related',
            type='string',
            help='exclude a package or specific model when searching for related objects (format: app_label or app_label.model)'),
        make_option('--exclude-field',
            action='append',
            dest='exclude_field',
            type='string',
            help='exclude field types from ever appearing in output (format: app_label or app_label.model)'),
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
        self.exclude_related = options.get('exclude_related') or []
        self.exclude_fields = options.get('exclude_field') or []

        qs = model_class.objects.all().filter(**filters)
        qs = qs.exclude(**excludes)
        return qs

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError, 'Error: modeler only accepts one model argument'

        # get a list of objects to start from
        roots = self.parse_args(*args, **options)
        if len(roots) < 1:
            print('No models found.', file=sys.stderr)
        else:
            modeler = Modeler(query_related=self.query_related,
                              exclude_related=self.exclude_related,
                              exclude_fields=self.exclude_fields)
            print(modeler.generate(*roots))
