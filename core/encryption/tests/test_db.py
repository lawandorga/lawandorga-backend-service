from core.encryption.models import Keyring
from core.tests import test_helpers


def test_storing_and_loading(db):
    org_user = test_helpers.create_raw_org_user(save=True)
    group = test_helpers.create_raw_group(org=org_user.org)
    group.save()

    group.add_member(org_user)
    keyring = org_user.keyring
    keyring.store()

    new_keyring = Keyring.objects.get(pk=keyring.pk).load()
    assert len(new_keyring._group_keys) == 1

    group.remove_member(org_user)
    newer_keyring = Keyring.objects.get(pk=keyring.pk).load()
    assert len(newer_keyring._group_keys) == 0
