import json

import pytest
from django.test import Client

from apps.core.models import Org
from apps.seedwork import test_helpers as data

from ...fixtures import create_permissions
from ...static import PERMISSION_ADMIN_MANAGE_GROUPS
from ..models import Group


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def group(db, org):
    g = Group.objects.create(name="Test Group", from_rlc=org)
    yield g


@pytest.fixture
def user_2(db, org):
    user_2 = data.create_rlc_user(email="dummy2@law-orga.de", name="Dummy 2", rlc=org)
    yield user_2


@pytest.fixture
def user(db, group, user_2, org):
    user_1 = data.create_rlc_user(rlc=org)
    org.generate_keys()
    create_permissions()
    group.members.add(user_1["rlc_user"])
    group.save()
    yield user_1


def test_list_users(user, group, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/groups/{}/users/".format(group.id))
    # response_data = response.json()
    assert response.status_code == 200


def test_add_member(user, group, db, user_2):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    response = c.post(
        "/api/groups/{}/add_member/".format(group.id),
        data=json.dumps({"new_member": user_2["rlc_user"].id}),
        content_type="application/json",
    )
    # response_data = response.json()
    assert response.status_code == 200


def test_add_member_permission_error(user, group, db, user_2):
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/groups/{}/add_member/".format(group.id),
        data=json.dumps({"new_member": user_2["rlc_user"].id}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_remove_member(user, group, db, user_2):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group.add_member(user_2["rlc_user"])
    response = c.post(
        "/api/groups/{}/remove_member/".format(group.id),
        data=json.dumps({"member": user_2["rlc_user"].id}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_add_member_fails_different_org(user, group, db):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    org2 = Org.objects.create(name="Another")
    another_user = data.create_rlc_user(
        email="another@law-orga.de", name="Another", rlc=org2
    )
    response = c.post(
        "/api/groups/{}/add_member/".format(group.id),
        data=json.dumps({"new_member": another_user["rlc_user"].id}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_add_member_already_member(user, group, db, user_2):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group.add_member(user_2["rlc_user"])
    response = c.post(
        "/api/groups/{}/add_member/".format(group.id),
        data=json.dumps({"new_member": user_2["rlc_user"].id}),
        content_type="application/json",
    )
    assert response.status_code == 400
