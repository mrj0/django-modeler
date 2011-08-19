from django.db import models
from django.contrib.auth.models import User

class TestModel(models.Model):
    """The main model for loan applications."""
    # if the user logs in this should be set
    user = models.ForeignKey(User, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    date_modified = models.DateTimeField(auto_now=True, null=False)

class RelatedToTestModel(models.Model):
    test_model = models.ForeignKey(TestModel)
    name = models.TextField()
