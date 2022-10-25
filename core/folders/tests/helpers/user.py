from uuid import uuid4

from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import UserKey


class UserObject:
    def __init__(self):
        self.slug = uuid4()
        (
            pr,
            pu,
            ve,
        ) = EncryptionPyramid.get_highest_asymmetric_encryption().generate_keys()
        self.key = UserKey(private_key=pr, public_key=pu, origin=ve)

    def get_key(self):
        return self.key
