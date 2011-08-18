from django.db.models.loading import get_apps, get_models

def generate_imports(*classes):
    """
    Given a list of model classes, generate import statements.
    """
    imports = []
    for cls in classes:
        for app in get_apps():
            if cls in get_models(app):
                imports.append('from {} import {}'.format(app.__name__, cls.__name__))
                break

    return imports + [
        'from decimal import Decimal',
        'import datetime',
    ]
