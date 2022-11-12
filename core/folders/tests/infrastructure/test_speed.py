import string
import time
import random

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
    data = ["".join([random.choice(string.ascii_letters) for i in range(0, 100)]).encode('utf-8') for i in range(0, L)]
    assert len(data) == L
    lboxes = []
    oboxes = []

    t1 = time.time()

    for i, _ in enumerate(data):
        o = OpenBox(data=data[i])
        l = keys[i].lock(o)
        lboxes.append(l)

    t2 = time.time()

    for i, _ in enumerate(data):
        l = lboxes[i]
        o = keys[i].unlock(l)
        oboxes.append(o)

    t3 = time.time()

    for i, _ in enumerate(data):
        assert data[i] == oboxes[i]

    print()
    print('encryption took', t2-t1, 'seconds.')
    print('decryption took', t3 - t2, 'seconds.')
