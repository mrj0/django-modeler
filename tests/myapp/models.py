from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING


class TestModel(models.Model):
    """The main model for loan applications."""
    # if the user logs in this should be set
    user = models.ForeignKey(User, null=True, blank=True, on_delete=DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    date_modified = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        app_label = 'myapp'


class RelatedToTestModel(models.Model):
    test_model = models.ForeignKey(TestModel, DO_NOTHING)
    name = models.TextField()

    class Meta:
        app_label = 'myapp'
