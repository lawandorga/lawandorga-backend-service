import pytest

from core.auth.models import OrgUser
from core.org.models import Group
from core.org.use_cases.group import create_group
from core.permissions.static import PERMISSION_ADMIN_MANAGE_GROUPS
from core.seedwork import test_helpers


@pytest.fixture
def user():
    user = test_helpers.create_raw_org_user()
    yield user


@pytest.fixture
def group():
    user = test_helpers.create_raw_org_user()
    group = test_helpers.create_raw_group(org=user.org)
    yield group


def test_group_update_information(group):
    group.update_information(name="New Name", description="New Description")
    assert group.name == "New Name" and group.description == "New Description"
    group.update_information(None, None)
    assert group.name == "New Name" and group.description == "New Description"


def test_add_member_and_remove(db, group, user):
    user.user.save()
    user.org.save()
    user.save()
    group.add_member(user)
    group.generate_keys()
    group.save()
    group.remove_member(user)
    assert not group.has_member(user)


def test_add_member_is_saved(db, group, user):
    user.org.save()
    user.user.save()
    user.save()
    user = OrgUser.objects.get(pk=user.pk)
    group.add_member(user)
    group.save()
    group = Group.objects.get(pk=group.pk)
    assert user.id in group.member_ids
    group.save()
    group = Group.objects.get(pk=group.pk)
    assert user.id in group.member_ids


def test_group_create_creates_keys(db):
    user = test_helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group = create_group(user, "Test Group", None)
    assert len(group.keys) == 1, group.keys
    assert group.has_keys(user)


def test_group_add_member_gets_key(db):
    user = test_helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group = create_group(user, "Test Group", None)
    user2 = test_helpers.create_org_user(email="dummy2@law-orga.de", rlc=user.org)[
        "org_user"
    ]
    group.add_member(user2, user)
    assert len(group.keys) == 2, group.keys
    assert group.has_keys(user2)


def test_group_remove_member_removes_key(db):
    user = test_helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group = create_group(user, "Test Group", None)
    user2 = test_helpers.create_org_user(email="dummy2@law-orga.de", rlc=user.org)[
        "org_user"
    ]
    group.add_member(user2, user)
    group.remove_member(user)
    assert len(group.keys) == 1, group.keys
    assert not group.has_keys(user)


def test_invalidate_keys(db):
    user = test_helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_GROUPS)
    group = create_group(user, "Test Group", None)
    group.invalidate_keys_of(user)
    assert not group.has_valid_keys(user)
