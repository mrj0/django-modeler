================
 Django-Modeler
================

Django-modeler generates ORM code from an object instance, optionally including foreign key dependencies.

----------
 Example
----------

Modeler adds a management command to Django:

::

    $ python manage.py modeler myapp.testmodel
    from myapp.models import TestModel
    from django.contrib.auth.models import User
    from decimal import Decimal
    import datetime


    user1, created = User.objects.get_or_create(
        id=1,
        username=u'mike',
        first_name=u'',
        last_name=u'',
        email=u'mike@localhost.com',
        password=u'sha1$911c9$614a16c3c074f2972e14efbe97f4fa92b266b93f',
        is_staff=True,
        is_active=True,
        is_superuser=True,
        last_login=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
        date_joined=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
    )

    testmodel1, created = TestModel.objects.get_or_create(
        id=1,
        user=user1,
    )

As requested, modeler found the TestModel instances and generated ORM code to recreate it (if it doesn't already
exist). Modeler also generated code for the User object since it was referenced by TestModel.

----------
 Why?
----------

This is a much nicer way of including test data. You probably already have a working site and some data for
production, but ``dumpdata`` will serialize the data for an entire app. That's too much just to write a quick test!

Many people end up with an old, out-of-date copy of their production data in their test fixtures that nobody dares to change.
And because fixtures can be a pain to keep up to date with site changes, it's common place to see a bunch of tests
depend on the same fixtures. Sometimes entire projects will depend on just one or two fixtures.

Unfortunately, if a refactor needs a fixture change due to model changes, changing the fixture could cause other tests to fail
that are unrelated to the refactor. Worse, it's difficult to edit the json directly, cumbersome to load and modify
it, and refactoring tools won't update fixtures.

Instead, it's better to have each test use it's own data unrelated to other apps in the project. Django-modeler
makes this easier to handle by generating Django ORM code that can be included in tests (or for other purposes).

----------
 Install
----------

To get this awesome for your very own, ``pip install django-modeler`` or ``python setup.py install`` from source.

Next, add ``django_modeler`` to your INSTALLED_APPS in ``settings.py``, like so:

::

    INSTALLED_APPS = (
        # other apps
        'django_modeler',
        # other apps
    )

----------
 USAGE
----------

Modeler supports a few command line options:

::

    Usage: manage.py modeler [options] <model [filter option] [filter option] ...>

    Writes data to ORM code to the console

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=all output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Print traceback on exception
      -f FILTER, --filter=FILTER
                            Filter objects
      -e EXCLUDE, --exclude=EXCLUDE
                            Exclude objects
      -r RELATED, --related=RELATED
                            number of object relationship levels to pull (does not
                            resolve circular references).
      --exclude-related=EXCLUDE_RELATED
                            exclude a package or specific model when searching for
                            related objects (format: app_label or app_label.model)
      --exclude-field=EXCLUDE_FIELD
                            exclude field types from ever appearing in output
                            (format: app_label or app_label.model)
      --version             show program's version number and exit
      -h, --help            show this help message and exit

Most important is the name of the model to start with. Modeler works by starting at an object instance and building
a dependency tree from that point. The tree can have many starting points, or it can start from a single instance.
The easiest way to filter for a single object is by using the `-f` filter. For example:

::

    $ python manage.py modeler auth.user -f pk=1
    from django.contrib.auth.models import User
    from decimal import Decimal
    import datetime
    
    user1, created = User.objects.get_or_create(
        id=1,
        username=u'mike',
        first_name=u'',
        last_name=u'',
        email=u'mike@localhost.com',
        password=u'sha1$911c9$614a16c3c074f2972e14efbe97f4fa92b266b93f',
        is_staff=True,
        is_active=True,
        is_superuser=True,
        last_login=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
        date_joined=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
    )


The `-f filter` and `-e exclude` options are fed directly to Django's ORM filter and exclude methods on QuerySet_
and support the same options.

.. _QuerySet: https://docs.djangoproject.com/en/dev/ref/models/querysets/#django.db.models.query.QuerySet.filter

With the `-r related` option, Modeler will attempt to also use ForeignKey references in it's output. In the example above,
pulling the auth.user instance only found a single object to serialize. But given the same command with a related depth
of 1, Modeler will find more objects that reference this particular user instance:

::

    $ python manage.py modeler auth.user -f pk=1 -r1
    from django.contrib.auth.models import User
    from myapp.models import TestModel
    from decimal import Decimal
    import datetime


    user1, created = User.objects.get_or_create(
        id=1,
        username=u'mike',
        first_name=u'',
        last_name=u'',
        email=u'mike@localhost.com',
        password=u'sha1$911c9$614a16c3c074f2972e14efbe97f4fa92b266b93f',
        is_staff=True,
        is_active=True,
        is_superuser=True,
        last_login=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
        date_joined=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
    )

    testmodel1, created = TestModel.objects.get_or_create(
        id=1,
        user=user1,
    )

With `-r2` Modeler will find another object instance that depends on the TestModel in the above:

::

    $ python manage.py modeler auth.user -f pk=1 -r2
    from myapp.models import RelatedToTestModel
    from django.contrib.auth.models import User
    from myapp.models import TestModel
    from decimal import Decimal
    import datetime


    user1, created = User.objects.get_or_create(
        id=1,
        username=u'mike',
        first_name=u'',
        last_name=u'',
        email=u'mike@localhost.com',
        password=u'sha1$911c9$614a16c3c074f2972e14efbe97f4fa92b266b93f',
        is_staff=True,
        is_active=True,
        is_superuser=True,
        last_login=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
        date_joined=datetime.datetime(2011, 8, 18, 20, 39, 14, 352576),
    )

    testmodel1, created = TestModel.objects.get_or_create(
        id=1,
        user=user1,
    )

    relatedtotestmodel1, created = RelatedToTestModel.objects.get_or_create(
        id=1,
        test_model=testmodel1,
        name=u'related_one',
    )

    relatedtotestmodel2, created = RelatedToTestModel.objects.get_or_create(
        id=2,
        test_model=testmodel1,
        name=u'related_two',
    )

Other options are ``--exclude-related`` and ``--exclude-field``. These both require an app_label.model argument.
Exclude related will ignore models found that match the app_label or model name when Modeler is searching
foreign key relationships, like in the above example both TestModel and RelatedToTestModel were found during the related
search.

Using ``--exclude-field`` prevents a model or app from ever showing up in the output, regardless of how it was found.

------------
 LIMITATIONS
------------

At this time, Modeler does not attempt to resolve circular dependencies when using `-r`. It may be necessary to limit
the depth that Modeler will travel in order to avoid an exception because of the model dependencies.

-------------------------
 WHAT CAN I DO WITH IT?
-------------------------

The original use case was to create test data. Use Modeler to create a `data.py` file in a tests folder:

::

    $ python manage.py modeler auth.user -f pk=1 -r2 > tests/data.py

`data.py` probably needs a `load()` method. The tests_ are a good example of this style usage.

.. _tests: https://github.com/mrj0/django-modeler/blob/master/tests/myapp/tests/data.py

Next, in the test that requires this data, add a setupUp method to load and use the data:

::

    def setUp(self):
        data.load()


------------
 SUPPORT
------------

Please use Github_.

.. _Github: https://github.com/mrj0/django-modeler

