from uuid import uuid4

from core.encryption.models import Keyring
from core.encryption.types import ObjectTypes
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.seedwork import test_helpers


def test_storing_and_loading(db):
    org_user = test_helpers.create_raw_org_user(save=True)
    group = test_helpers.create_raw_group(org=org_user.org)
    group.save()

    group.add_member(org_user)
    keyring = org_user.keyring
    id = uuid4()
    keyring.add_object_key(
        id, ObjectTypes.FOLDER, SymmetricKey.generate(SymmetricEncryptionV1)
    )
    keyring.add_object_key_for_group(group, id, ObjectTypes.FOLDER)
    keyring.store()

    new_keyring = Keyring.objects.get(pk=keyring.pk).load()
    assert len(new_keyring._object_keys) == 1
    assert len(new_keyring._group_keys) == 1
    assert len(new_keyring._group_keys[0]._object_keys) == 1
    new_keyring.remove_object_key_for_group(group, id, ObjectTypes.FOLDER)
    new_keyring.store()

    newer_keyring = Keyring.objects.get(pk=keyring.pk).load()
    assert len(newer_keyring._object_keys) == 1
    assert len(newer_keyring._group_keys) == 1
    assert len(newer_keyring._group_keys[0]._object_keys) == 0
    new_keyring.remove_group_key(group)
    new_keyring.store()

    final_keyring = Keyring.objects.get(pk=keyring.pk).load()
    assert len(final_keyring._object_keys) == 1
    assert len(final_keyring._group_keys) == 0
