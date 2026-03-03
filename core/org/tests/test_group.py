import json
from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from core.models import Org
from core.org.models import Group
from core.org.use_cases.group import add_member_to_group
from core.permissions.static import PERMISSION_ADMIN_MANAGE_GROUPS
from core.seedwork.use_case_layer.error import UseCaseError
from core.tests import test_helpers as test_helpers


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def user(db, org):
    user_1 = test_helpers.create_org_user(org=org)
    org.generate_keys()
    user_1["org_user"].keyring.store()
    yield user_1


@pytest.fixture
def group(db, org, user):
    g = Group.create(
        name="Test Group", org=org, description="Just testing.", by=user["org_user"]
    )
    yield g


@pytest.fixture
def user_2(db, org):
    user_2 = test_helpers.create_org_user(
        email="dummy2@law-orga.de", name="Dummy 2", org=org
    )
    yield user_2


@pytest.fixture
def user_3(db, org):
    user_3 = test_helpers.create_org_user(
        email="dummy3@law-orga.de", name="Dummy 3", org=org
    )
    yield user_3


def test_list_users(user, group, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/org/query/group/{}/".format(group.id))
    assert response.status_code == 200 and "members" in response.json()


def test_add_member(user, group, db, user_2):
    c = Client()
    c.login(**user)
    user["org_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {
                "new_member_id": user_2["org_user"].id,
                "group_id": group.id,
                "action": "org/add_member_to_group",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200, response.json()


def test_add_member_permission_error(user, group, db, user_2):
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {
                "new_member_id": user_2["org_user"].id,
                "group_id": group.id,
                "action": "org/add_member_to_group",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400, response.json()


def test_remove_member(user, group, db, user_2, user_3):
    c = Client()
    c.login(**user)
    user["org_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group.add_member(user_2["org_user"], by=user["org_user"])
    group.add_member(user_3["org_user"], by=user["org_user"])
    group.save()
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {
                "member_id": user_2["org_user"].id,
                "group_id": group.id,
                "action": "org/remove_member_from_group",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200, response.json()


def test_add_member_fails_different_org(user, group, db):
    c = Client()
    c.login(**user)
    user["org_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    org2 = Org.objects.create(name="Another")
    another_user = test_helpers.create_org_user(
        email="another@law-orga.de", name="Another", org=org2
    )
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {
                "new_member_id": another_user["org_user"].pk,
                "group_id": group.id,
                "action": "org/add_member_to_group",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400, response.json()


def test_add_member_already_member(user, group, db, user_2):
    c = Client()
    c.login(**user)
    user["org_user"].grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group.add_member(user_2["org_user"], by=user["org_user"])
    group.save()
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {
                "new_member_id": user_2["org_user"].id,
                "group_id": group.id,
                "action": "org/add_member_to_group",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400, response.json()


def test_add_member_fails_if_user_never_logged_in_for_over_a_year(db):
    user = test_helpers.create_raw_org_user(save=True)
    g = test_helpers.create_raw_group(
        name="Test Group",
        org=user.org,
        description="Just testing.",
        members=[user],
        save=True,
    )

    user.grant(PERMISSION_ADMIN_MANAGE_GROUPS)

    stale_user = test_helpers.create_raw_org_user(
        email="stale@law-orga.de", name="Stale User", org=user.org, save=True
    )
    stale_user_user = stale_user.user
    stale_user_user.created = timezone.now() - timedelta(days=366)
    stale_user_user.last_login = None
    stale_user_user.save(update_fields=["created", "last_login"])

    with pytest.raises(UseCaseError):
        add_member_to_group(
            __actor=user,
            group_id=g.pk,
            new_member_id=stale_user.user.pk,
        )
