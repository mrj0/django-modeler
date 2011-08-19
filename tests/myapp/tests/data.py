from myapp.models import TestModel
from django.contrib.auth.models import User
from decimal import Decimal
import datetime
from tests.myapp.models import RelatedToTestModel

def load():
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

    related1, created = RelatedToTestModel.objects.get_or_create(
        id=1,
        name='related_one',
        test_model=testmodel1,
    )

    related2, created = RelatedToTestModel.objects.get_or_create(
        id=2,
        name='related_two',
        test_model=testmodel1,
    )
