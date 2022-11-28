import pickle

from core.auth.domain.user_key import UserKey
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
    SymmetricKey,
)


def assert_key_works(key):
    o1 = OpenBox(data=b"Secret")
    l1 = key.lock(o1)
    o2 = key.unlock(l1)
    assert o1 == o2


def test_user_key_create_from_unecrypted_works():
    key = AsymmetricKey.generate()
    u = UserKey.create_from_dict(
        {
            "private_key": key.get_private_key().decode("utf-8"),
            "public_key": key.get_public_key(),
            "origin": key.origin,
            "type": "USER",
        }
    )
    assert_key_works(u.key)


def test_user_key_create_from_encrypted_works():
    key = AsymmetricKey.generate()
    password = "abc123"
    s = SymmetricKey(key=OpenBox(data=password.encode("utf-8")), origin="S1")
    enc_private_key = s.lock(key.get_private_key())
    enc_key = EncryptedAsymmetricKey(
        enc_private_key=enc_private_key,
        public_key=key.get_public_key(),
        origin=key.origin,
    )
    u1 = UserKey.create_from_dict({"key": enc_key.as_dict(), "type": "USER"})
    u2 = u1.decrypt_self(password)
    assert_key_works(u2.key)


def test_user_key_to_dict_and_from_dict_works():
    password = "pw12"
    key = AsymmetricKey.generate()
    u1 = UserKey(key=key)
    o1 = OpenBox(data=b"Secret")
    l1 = u1.key.lock(o1)
    u2 = u1.encrypt_self(password)
    u3 = u2.as_dict()
    u4 = UserKey.create_from_dict(u3)
    u5 = u4.decrypt_self(password)
    o2 = u5.key.unlock(l1)
    assert o1 == o2


def test_user_key_can_encrypt_and_decrypt():
    key = AsymmetricKey.generate()
    u1 = UserKey(key=key)
    assert_key_works(u1.key)


def test_key_is_pickleable():
    key = AsymmetricKey.generate()
    u1 = UserKey(key=key)
    u2 = pickle.dumps(u1)
    u3 = pickle.loads(u2)
    assert_key_works(u3.key)
