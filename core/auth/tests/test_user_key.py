from core.auth.domain.user_key import UserKey
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.keys import AsymmetricKey


def assert_key_works(key):
    o1 = OpenBox(b"Secret")
    l1 = key.lock(o1)
    o2 = key.unlock(l1)
    assert o1 == o2


def test_user_key_create_from_unecrypted_works():
    key = AsymmetricKey.generate()
    u = UserKey.create_from_dict(
        {
            "private_key": key.get_private_key(),
            "public_key": key.get_public_key(),
            "origin": key.origin,
        }
    )
    assert_key_works(u.key)


def test_user_key_create_from_encrypted_works():
    pass


def test_user_key_to_dict_and_from_dict_works():
    pass


def test_user_key_can_encrypt_and_decrypt():
    pass
