from __future__ import print_function
from optparse import make_option

from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model, DateField, DateTimeField, ForeignKey
from django.db.models.fields.related import OneToOneField
from django.utils.datastructures import SortedDict

from django_modeler.api import generate_imports, get_object_dependencies, generate_orm

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
            action='store_true',
            dest='related',
            default=False,
            help='query related objects (warning: can take some time)'),
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

        # keep building lists of FK dependencies until we get to the leaf
        roots = self.parse_args(*args, **options)
        level = roots
        stack = SortedDict()
        map(stack.__setitem__, roots, [])

        while True:
            deps = []
            for obj in level:
                deps += get_object_dependencies(obj, related=self.query_related)

            level = []
            for dep in deps:
                if dep in stack:
                    # looks weird but with the sorteddict, replacing a
                    # key preserves the original order
                    del stack[dep]
                else:
                    # only loop instances we haven't seen before
                    level.append(dep)
                stack[dep] = None

            if len(deps) < 1:
                break

        # add FK classes to set for generating imports
        classes = set().union([obj.__class__ for obj in stack.keys()])
        map(print, generate_imports(*classes))
        print()
        print()

        objects = defaultdict(list)
        for obj in reversed(stack.keys()):
            if obj.pk in objects[obj]:
                continue

            print(generate_orm(obj, indent=self.indent))
            print()

        # handle
