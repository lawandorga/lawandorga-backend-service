import json

from django.test import Client
import pytest

from apps.core.models import Org
from apps.static import test_helpers as data

from ..models import Group


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def group(db, org):
    g = Group.objects.create(name='Test Group', from_rlc=org)
    yield g


@pytest.fixture
def user(db, group, org):
    user_1 = data.create_rlc_user(rlc=org)
    org.generate_keys()
    group.group_members.add(user_1['user'])
    group.save()
    yield user_1


def test_list_users(user, group, db):
    c = Client()
    c.login(**user)
    response = c.put("/api/groups/{}/users/".format(group.id))
    # response_data = response.json()
    assert response.status_code == 200
