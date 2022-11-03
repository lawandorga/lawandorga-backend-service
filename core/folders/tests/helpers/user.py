from uuid import uuid4

from core.folders.domain.value_objects.keys import AsymmetricKey


class UserObject:
    def __init__(self):
        self.slug = uuid4()
        self.key = AsymmetricKey.generate()

    def get_key(self):
        return self.key
