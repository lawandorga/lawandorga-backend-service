import pytest

from core.auth.models import RlcUser
from core.rlc.models import Group
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
    group.save()
    group.add_member(user)
    group.remove_member(user)
    assert not group.has_member(user)


def test_add_member_is_saved(db, group, user):
    user.org.save()
    user.user.save()
    user.save()
    user = RlcUser.objects.get(pk=user.pk)
    group.add_member(user)
    group.save()
    group = Group.objects.get(pk=group.pk)
    assert user.id in group.member_ids
    group.save()
    group = Group.objects.get(pk=group.pk)
    assert user.id in group.member_ids
