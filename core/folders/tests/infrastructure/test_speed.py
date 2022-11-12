import random
import string
import time

import pytest

from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.keys import SymmetricKey
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


@pytest.fixture
def real_encryption(encryption_reset):
    EncryptionWarehouse.add_asymmetric_encryption(SymmetricEncryptionV1)


@pytest.fixture
def keys(real_encryption):
    keys = []
    key = SymmetricKey.generate()
    for i in range(0, 5000):
        keys.append(key)
    yield keys


def disable_test_speed(keys):
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

    print()
    print("encryption took", t2 - t1, "seconds.")
    print("decryption took", t3 - t2, "seconds.")
