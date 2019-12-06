import argparse
import sys

import django
from django.apps import apps

from django_modeler.modeler import Modeler


def main():
    parser = argparse.ArgumentParser(description='Generate django ORM code')
    parser.add_argument(
        '-f', '--filter',
        action='append',
        dest='filter',
        type=str,
        help='Filter objects')
    parser.add_argument(
        '--in',
        action='append',
        dest='filter_in',
        type=str,
        help='Filter objects using an IN list (ex: "--in pk=259576,1232,213")')
    parser.add_argument(
        '-e', '--exclude',
        action='append',
        dest='exclude',
        type=str,
        help='Exclude objects')
    parser.add_argument(
        '-r', '--related',
        action='store',
        dest='related',
        type=int,
        default=0,
        help='number of object relationship levels to pull (does not resolve circular references).')
    parser.add_argument(
        '--exclude-related',
        action='append',
        dest='exclude_related',
        type=str,
        help='exclude a package or specific model when searching for related objects (format: app_label or app_label.model)')
    parser.add_argument(
        '--exclude-field',
        action='append',
        dest='exclude_field',
        type=str,
        help='exclude field types from ever appearing in output (format: app_label or app_label.model)')
    parser.add_argument(
        dest='name',
        nargs=1,
        help='<APP>.<MODEL> required'
    )

    args = parser.parse_args()

    django.setup()

    # get a list of objects to start from
    name = args.name
    model_class = apps.get_model(*name.split('.'))
    if not model_class:
        raise argparse.ArgumentError('Error: model not found: {0}'.format(name))

    filters = {}
    for arg in args.filter or []:
        if '=' not in arg:
            raise argparse.ArgumentError('Filter syntax is name=value. Invalid argument {0}'.format(arg))
        filters.__setitem__(*arg.split('=', 1))
    for arg in args.filter_in or []:
        if '=' not in arg:
            raise argparse.ArgumentError('Filter syntax is name=value. Invalid argument {0}'.format(arg))
        name, values = arg.split('=', 1)
        filters['{0}__in'.format(name)] = [_f for _f in values.split(',') if _f]
    excludes = {}
    for arg in args.exclude or []:
        if '=' not in arg:
            raise argparse.ArgumentError('Exclude syntax is name=value. Invalid argument {0}'.format(arg))
        excludes.__setitem__(*arg.split('=', 1))

    query_related = args.related
    exclude_related = args.exclude_related or []
    exclude_fields = args.exclude_field or []

    qs = model_class.objects.all().filter(**filters)
    roots = qs.exclude(**excludes)

    if len(roots) < 1:
        print('No models found.', file=sys.stderr)
    else:
        modeler = Modeler(query_related=query_related,
                          exclude_related=exclude_related,
                          exclude_fields=exclude_fields)
        print(modeler.generate(*roots))
