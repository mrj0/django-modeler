from _collections import defaultdict
from django.db.models.fields import DateField, DateTimeField
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.db.models.loading import get_apps, get_models
from django.utils.datastructures import SortedDict
from graph import Digraph

def generate(*roots, **kw):
    """
    Generate ORM code for roots.
    """
    query_related = 0
    if 'query_related' in kw:
        query_related = int(kw['query_related'])
        del kw['query_related']
    indent = 4
    if 'indent' in kw:
        query_related = int(kw['indent'])
        del kw['indent']
    exclude_related_apps = []
    if 'exclude_related_apps' in kw:
        exclude_related_apps = kw['exclude_related_apps']
        del kw['exclude_related_apps']
    exclude_related_models = defaultdict(list)
    if 'exclude_related_models' in kw:
        models = kw['exclude_related_models']
        del kw['exclude_related_models']
        for model in models:
            app_label, name = model.split('.')
            exclude_related_models[app_label].append(name)

    if len(kw) > 0:
        raise TypeError, 'Unexpected function arguments {}'.format(kw.keys())
    
    level = roots
    graph = Digraph(roots)

    while len(level) > 0:
        next_level = []

        for obj in level:
            deps = get_object_dependencies(obj)
            next_level += [dep for dep in deps if dep not in graph]
            graph.arc(obj, *deps)

            if query_related > 0:
                related = get_related_objects(
                    obj,
                    exclude_apps=exclude_related_apps,
                    exclude_models=exclude_related_models)
                for dep in related:
                    next_level += [dep for dep in related if dep not in graph]
                    # these are different. since they're related objects, they depend on obj
                    graph.arc(dep, obj)
                deps += related
        query_related -= 1

        level = set(next_level)

    # add FK classes to set for generating imports
    classes = set().union([obj.__class__ for obj in graph.keys()])
    code = u''
    for stmt in generate_imports(*classes):
        code += stmt + '\n'
    code += '\n\n'

#    visualize(graph)
    for obj in graph.toposort2():
        code += generate_orm(obj, indent=indent) + '\n\n'
    return code

def visualize(graph):
    import json
    # copy graph
    names = SortedDict()
    for key, deps in graph.items():
        names[object_name(key)] = [object_name(d) for d in deps]
    print json.dumps(names, indent=2)

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

def get_object_dependencies(obj):
    """
    Get all model dependencies for the instance.
    """
    deps = []

    # get the names of FK fields
    for name in [f.name for f in obj._meta.fields if f.rel]:
        dep = getattr(obj, name)
        if dep:
            deps.append(dep)
    return deps

def get_related_objects(obj, exclude_apps=None, exclude_models=None):
    """
    Try to get foreign key dependencies of obj
    """
    deps = []
    exclude_apps = exclude_apps or []
    exclude_models = exclude_models or {}
    for related in obj._meta.get_all_related_objects():
        if isinstance(related.field, OneToOneField):
            pass
        elif isinstance(related.field, ForeignKey):
            accessor = related.get_accessor_name()
            manager = getattr(obj, accessor)
            for dep in manager.all():
                app_label = dep._meta.app_label
                model_name = dep._meta.object_name.lower()
                if not app_label in exclude_apps and not model_name in exclude_models.get(app_label, []):
                    deps.append(dep)
    return deps

def object_name(obj):
    return u'{0}{1}'.format(obj._meta.object_name.lower(), obj.pk)

def generate_orm(obj, indent=4):
    """
    Write django ORM code for a given instance.
    """
    code = u'{0}, created = {1}.objects.get_or_create(\n'.format(object_name(obj), obj._meta.object_name)

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
