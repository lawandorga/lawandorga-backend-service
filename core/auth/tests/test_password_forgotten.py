from core.auth.use_cases.user import set_password_of_myself
from core.org.models.group import Group
from core.org.use_cases.group import correct_group_keys_of_others
from core.seedwork import test_helpers


def test_group_keys_invalidated(db):
    user1 = test_helpers.create_org_user()["rlc_user"]
    user2 = test_helpers.create_org_user(email="tester@law-orga.de", rlc=user1.org)[
        "rlc_user"
    ]

    group = Group.create(org=user1.org, name="Test Group", description="")
    group.save()
    group.add_member(user1)
    group.generate_keys()
    group.add_member(user2, user1)
    assert group.has_keys(user1)
    assert group.has_keys(user2)

    set_password_of_myself(user2.user, "password")
    group.refresh_from_db()
    group.get_decryption_key(user1)
    assert not group.has_valid_keys(user2)
    try:
        group.get_decryption_key(user2)
    except Exception as e:
        assert "Padding" not in str(e)


def test_group_keys_fixed_with_unlock(db):
    user1 = test_helpers.create_org_user()["rlc_user"]
    user2 = test_helpers.create_org_user(email="tester@law-orga.de", rlc=user1.org)[
        "rlc_user"
    ]

    group = Group.create(org=user1.org, name="Test Group", description="")
    group.save()
    group.add_member(user1)
    group.generate_keys()
    group.add_member(user2, user1)
    assert group.has_keys(user1)
    assert group.has_keys(user2)

    set_password_of_myself(user2.user, "password")
    group.refresh_from_db()
    group.get_decryption_key(user1)
    assert not group.has_valid_keys(user2)

    correct_group_keys_of_others(user1)
    group.refresh_from_db()
    assert group.has_valid_keys(user2)
