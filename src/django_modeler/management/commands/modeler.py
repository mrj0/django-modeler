from __future__ import print_function
from optparse import make_option
from collections import namedtuple

import logging

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model, DateField, DateTimeField
from django_modeler.api.generator import generate_imports

from collections import defaultdict

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
        )

    def parse_args(self, *args, **options):
        name = args[0]
        model_class = get_model(*name.split('.'))
        if not model_class:
            raise CommandError, 'Error: model not found: {}'.format(name)
        logging.debug('Got model class {}'.format(model_class))

        filters = {}
        for arg in options.get('filter') or []:
            if '=' not in arg:
                raise CommandError, 'Filter syntax is name=value. Invalid argument {}'.format(arg)
            filters.__setitem__(*arg.split('=', 1))
        excludes = {}
        for arg in options.get('exclude') or []:
            if '=' not in arg:
                raise CommandError, 'Exclude syntax is name=value. Invalid argument {}'.format(arg)
            excludes.__setitem__(*arg.split('=', 1))

        qs = model_class.objects.all().filter(**filters)
        qs = qs.exclude(**excludes)
        return qs

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError, 'Error: modeler only accepts on model argument'

        # keep building lists of FK dependencies until we get to the leaf
        roots = self.parse_args(*args, **options)
        level = roots
        stack = []
        classes = set().union([r.__class__ for r in roots])

        while True:
            deps = []
            for obj in level:
                # add FK classes to set for generating imports
                classes = classes.union([f.rel.to for f in obj._meta.fields if f.rel])
                # get the names of FK fields
                for name in [f.name for f in obj._meta.fields if f.rel]:
                    dep = getattr(obj, name)
                    if dep:
                        deps.append(dep)
            stack.append(level)
            level = deps

            if len(deps) < 1:
                break

        map(print, generate_imports(*classes))
        print()
        print()

        objects = defaultdict(list)
        for level in reversed(stack):
            for obj in reversed(level):
                if obj.pk in objects[obj]:
                    continue

                print('{}{}, created = {}.objects.get_or_create('.format(
                    obj._meta.object_name.lower(),
                    obj.pk,
                    obj._meta.object_name))

                postfields = []
                for field in obj._meta.fields:
                    if field.name.startswith('_'):
                        continue
                    if isinstance(field, DateField) and (field.auto_now or field.auto_now_add):
                        postfields.append(field)
                        continue
                    if isinstance(field, DateTimeField) and (field.auto_now or field.auto_now_add):
                        postfields.append(field)
                        continue

                    print(' ' * self.indent, field.name, '=', end='', sep='')
                    if field.rel and field.rel.to:
                        rel = getattr(obj, field.name)
                        if rel:
                            print('{}{}'.format(rel._meta.object_name.lower(), rel.pk), end='')
                        else:
                            print('None', end='')
                    else:
                        print(repr(getattr(obj, field.name)), sep='', end='')
                    print(',')
                print(')')
                print()

        #print('classes', classes)
        #print('stack', stack)


