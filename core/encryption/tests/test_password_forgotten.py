import pytest

from core.auth.use_cases.user import set_new_password_of_myself
from core.encryption.usecases import optimize
from core.org.models.group import Group
from core.seedwork import test_helpers
from core.seedwork.domain_layer import DomainError


def test_group_keys_invalidated(db):
    user1 = test_helpers.create_org_user()["org_user"]
    user2 = test_helpers.create_org_user(email="tester@law-orga.de", org=user1.org)[
        "org_user"
    ]

    group = Group.create(org=user1.org, name="Test Group", description="", by=user1)
    group.add_member(user2, user1)
    assert user1.keyring._find_group_key(group.uuid) is not None
    assert user2.keyring._find_group_key(group.uuid) is not None

    set_new_password_of_myself(user2.user, "password")
    user1.refresh_from_db()
    key1 = user1.keyring._find_group_key(group.uuid)
    assert key1 and not key1.is_invalidated
    key2 = user2.keyring._find_group_key(group.uuid)
    assert key2 and key2.is_invalidated
    with pytest.raises(DomainError):
        user2.keyring.get_group_key(group.uuid)


def test_group_keys_fixed_with_unlock(db):
    user1 = test_helpers.create_org_user()["org_user"]
    user2 = test_helpers.create_org_user(email="tester@law-orga.de", org=user1.org)[
        "org_user"
    ]

    group = Group.create(org=user1.org, name="Test Group", description="", by=user1)
    group.add_member(user2, user1)
    assert user1.keyring._find_group_key(group.uuid) is not None
    assert user2.keyring._find_group_key(group.uuid) is not None

    set_new_password_of_myself(user2.user, "password")
    user1.refresh_from_db()
    assert user1.keyring._find_group_key(group.uuid) is not None
    key2 = user2.keyring._find_group_key(group.uuid)
    assert key2 and key2.is_invalidated

    optimize(user1)
    user2.keyring.load(force=True)
    new_key2 = user2.keyring._find_group_key(group.uuid)
    assert new_key2 and not new_key2.is_invalidated
