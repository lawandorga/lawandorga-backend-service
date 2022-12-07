import random
import string
import time

import pytest

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


@pytest.fixture
def real_encryption(encryption_reset):
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)


def generate_keys(L: int):
    keys = []
    key = SymmetricKey.generate()
    for i in range(0, L):
        keys.append(key)
    assert len(keys) == L
    return keys


def generate_data(L: int):
    data = [
        "".join([random.choice(string.ascii_letters) for _ in range(0, 100)]).encode(
            "utf-8"
        )
        for _ in range(0, L)
    ]
    assert len(data) == L
    return data


@pytest.fixture
def keys(real_encryption):
    yield generate_keys(5000)


def test_speed(keys):
    L = 1000
    data = [
        "".join([random.choice(string.ascii_letters) for i in range(0, 100)]).encode(
            "utf-8"
        )
        for i in range(0, L)
    ]
    assert len(data) == L
    lboxes = []
    oboxes = []

    t1 = time.time()

    for i, _ in enumerate(data):
        open_box = OpenBox(data=data[i])
        locked_box = keys[i].lock(open_box)
        lboxes.append(locked_box)

    t2 = time.time()

    for i, _ in enumerate(data):
        locked_box = lboxes[i]
        open_box = keys[i].unlock(locked_box)
        oboxes.append(open_box)

    t3 = time.time()

    for i, _ in enumerate(data):
        assert data[i] == oboxes[i]

    assert t2 - t1 < 1 and t3 - t2 < 1


def test_encryption_unicode():
    # test size
    L = 1000

    # data and keys
    data = generate_data(L)
    keys = generate_keys(L)

    # test no weird characters inside locked box
    for i in range(0, L):
        open_box = OpenBox(data=data[i])
        locked_box = keys[i].lock(open_box)
        locked_box_dict = locked_box.as_dict()
        if "\u0000" in locked_box_dict["enc_data"]:
            assert False

        locked_box_2 = LockedBox.create_from_dict(locked_box_dict)
        open_box_2 = keys[i].unlock(locked_box_2)
        assert open_box == open_box_2
