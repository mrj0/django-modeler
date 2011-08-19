from django.db.models.fields import DateField, DateTimeField
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.db.models.loading import get_apps, get_models

def generate_imports(*classes):
    """
    Given a list of model classes, generate import statements.
    """
    imports = []
    for cls in classes:
        for app in get_apps():
            if cls in get_models(app):
                imports.append('from {0} import {1}'.format(app.__name__, cls.__name__))
                break

    return imports + [
        'from decimal import Decimal',
        'import datetime',
    ]

def get_object_dependencies(obj, related=True):
    """
    Get all model dependencies for the instance.

    If related is True, will also attempt to get foreign key relationships as well.
    """
    deps = []

    # get the names of FK fields
    for name in [f.name for f in obj._meta.fields if f.rel]:
        dep = getattr(obj, name)
        if dep:
            deps.append(dep)

    if related:
        for related in obj._meta.get_all_related_objects():
            if isinstance(related.field, OneToOneField):
                pass
            elif isinstance(related.field, ForeignKey):
                accessor = related.get_accessor_name()
                manager = getattr(obj, accessor)
                for dep in manager.all():
                    deps.append(dep)
    return deps

def generate_orm(obj, indent=4):
    """
    Write django ORM code for a given instance.
    """
    code = '{0}{1}, created = {2}.objects.get_or_create(\n'.format(
        obj._meta.object_name.lower(),
        obj.pk,
        obj._meta.object_name)

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

        code += '{indent}{name}='.format(indent=(' ' * indent), name=field.name)
        if field.rel and field.rel.to:
            rel = getattr(obj, field.name)
            if rel:
                code += '{0}{1}'.format(rel._meta.object_name.lower(), rel.pk)
            else:
                code += 'None'
        else:
            code += repr(getattr(obj, field.name))
        code += ',\n'
    code += ')'
    return code
