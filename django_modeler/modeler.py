from __future__ import absolute_import
from collections import defaultdict
from django.db.models.fields import DateField, DateTimeField
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.db.models.loading import get_apps, get_models
from django.utils.datastructures import SortedDict
from django_modeler.graph import Digraph

class Modeler(object):
    def __init__(self, query_related=0, indent=4, exclude_related=None, exclude_fields=None):
        self.query_related = query_related
        self.indent = indent
        self.exclude_related_models = defaultdict(list)
        self.exclude_related_apps = []
        if exclude_related:
            for pair in exclude_related:
                if '.' in pair:
                    app_label, name = pair.split('.')
                    self.exclude_related_models[app_label].append(name)
                else:
                    self.exclude_related_apps.append(pair)

        # excluded fields encompass both related dependencies and field dependencies
        self.exclude_field_apps = list(self.exclude_related_apps)
        self.exclude_field_models = defaultdict(list, self.exclude_related_models)
        if exclude_fields:
            for pair in exclude_fields:
                if '.' in pair:
                    app_label, name = pair.split('.')
                    self.exclude_field_models[app_label].append(name)
                else:
                    self.exclude_field_apps.append(pair)

    def generate(self, *roots):
        """
        Generate ORM code for roots.
        """
        level = roots
        self.graph = Digraph(roots)

        query_related = self.query_related # shadows

        while level:
            next_level = set()
            graphkeys = set(self.graph.keys())

            for obj in level:
                deps = [dep for dep in self.get_object_dependencies(obj)
                            if not self.is_field_excluded(dep)]
                next_level = next_level.union(set(deps) - graphkeys)
                self.graph.arc(obj, *deps)

                if query_related > 0:
                    related = self.get_related_objects(obj)
                    next_level = next_level.union((set(related) - graphkeys))
                    for dep in related:
                        # these are different. since they're related objects, they depend on obj
                        self.graph.arc(dep, obj)
            query_related -= 1
            level = next_level

            # while level

        # add FK classes to set for generating imports
        classes = set().union([obj.__class__ for obj in self.graph.keys()])
        code = u''
        for stmt in self.generate_imports(*classes):
            code += stmt + '\n'
        code += '\n\n'

    #    visualize(graph)
        for obj in self.graph.toposort2():
            code += self.generate_orm(obj) + '\n\n'
        return code

    def is_field_excluded(self, dep):
        if not dep:
            return False
        model_name = dep._meta.object_name.lower()
        app_label = dep._meta.app_label
        return app_label in self.exclude_field_apps or \
               model_name in self.exclude_field_models[app_label]

    def visualize(self):
        import json
        # copy graph
        names = SortedDict()
        for key, deps in self.graph.items():
            names[self.object_name(key)] = [self.object_name(d) for d in deps]
        print json.dumps(names, indent=2)

    def generate_imports(self, *classes):
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

    def get_object_dependencies(self, obj):
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

    def get_related_objects(self, obj):
        """
        Try to get foreign key dependencies of obj
        """
        deps = []
        for related in obj._meta.get_all_related_objects():
            if isinstance(related.field, OneToOneField):
                pass
            elif isinstance(related.field, ForeignKey):
                accessor = related.get_accessor_name()
                manager = getattr(obj, accessor)
                for dep in manager.all():
                    app_label = dep._meta.app_label
                    model_name = dep._meta.object_name.lower()
                    if not app_label in self.exclude_related_apps and not model_name in self.exclude_related_models.get(app_label, []):
                        deps.append(dep)
        return deps

    def object_name(self, obj):
        return u'{0}{1}'.format(obj._meta.object_name.lower(), obj.pk)

    def generate_orm(self, obj):
        """
        Write django ORM code for a given instance.
        """
        code = u'{0}, created = {1}.objects.get_or_create(\n'.format(self.object_name(obj), obj._meta.object_name)

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
            if field.rel and field.rel.to:
                rel = getattr(obj, field.name)
                if self.is_field_excluded(rel):
                    continue

            code += '{indent}{name}='.format(indent=(' ' * self.indent), name=field.name)
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
