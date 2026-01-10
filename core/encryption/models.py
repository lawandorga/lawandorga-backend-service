from typing import TYPE_CHECKING, Union
from uuid import UUID

from django.conf import settings
from django.db import models, transaction

from core.auth.domain.user_key import UserKey
from core.auth.models import OrgUser
from core.auth.models.session import CustomSession
from core.encryption.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.encryption.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.encryption.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.seedwork.domain_layer import DomainError

from seedwork.functional import list_filter

if TYPE_CHECKING:
    from core.org.models.group import Group


class KeyNotFoundError(Exception):
    pass


class KeyringManager(models.Manager["Keyring"]):
    def load(self, user: OrgUser) -> "Keyring":
        keyring = (
            self.filter(user=user)
            .prefetch_related(
                "object_keys",
                "group_keys",
                "group_keys__group",
                "group_keys__group__object_keys",
            )
            .get()
        )
        keyring.load()
        return keyring


class Keyring(models.Model):
    @classmethod
    def create(cls, user: OrgUser | None, key: UserKey) -> "Keyring":
        keyring = Keyring()
        if user is not None:
            keyring = Keyring(user=user)
        keyring.key = key.as_dict()
        keyring._group_keys = []
        keyring._is_loaded = True
        return keyring

    user: models.OneToOneField["Keyring", OrgUser] = models.OneToOneField(
        OrgUser, on_delete=models.CASCADE, related_name="keyring"
    )
    key = models.JSONField(null=False, blank=True)
    decryption_key: AsymmetricKey | None = None

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = KeyringManager()

    if TYPE_CHECKING:
        _group_keys: list["GroupKey"]
        group_keys: models.QuerySet["GroupKey"]

    class Meta:
        verbose_name = "ENC_Keyring"
        verbose_name_plural = "ENC_Keyrings"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_loaded = False

    def __str__(self):
        if not hasattr(self, "user"):
            return "keyring: None;"
        return f"keyring: {self.user.email};"

    def __repr__(self):
        return self.__str__()

    @property
    def has_invalid_keys(self) -> bool:
        self.load()
        for gkey in self._group_keys:
            if gkey.is_invalidated:
                return True
        return False

    def load(self, force: bool = False) -> "Keyring":
        if self._is_loaded and not force:
            return self
        self._group_keys = list(self.group_keys.all())
        self._is_loaded = True
        return self

    def load_with_decryption_key(self) -> "Keyring":
        self.load()
        self.get_decryption_key()
        return self

    def save(self, *args, **kwargs):
        """
        Disabled to allow:
        - Easier in-memory testing (no accidental DB writes during tests)
        - Keyring acts as an aggregate (DDD): only Keyring should be saved, not its children directly
        - More predictable code: Keyring must be saved after critical actions, ideally atomically
        Note: GroupKey's ObjectKeys are an edge case and don't fit perfectly into this model.
        Use store() instead for persistence.
        """
        raise Exception("save is disabled use store() instead")

    def store(self):
        self.load()
        with transaction.atomic():
            super().save()
            self.group_keys.all().delete()
            GroupKey.objects.bulk_create(self._group_keys)

    def __get_session(self) -> CustomSession:
        session = (
            CustomSession.objects.filter(user_id=self.user.user_id)
            .order_by("-expire_date")
            .first()
        )

        if session is None:
            raise Exception(
                f"no session found for user '{self.user.user_id}' with last login '{self.user.user.last_login}'"
            )

        return session

    def __get_user_key_from_session(self) -> UserKey:
        session = self.__get_session()
        decoded = session.get_decoded()
        key = UserKey.create_from_unsafe_dict(decoded["user_key"])
        return key

    @staticmethod
    def get_dummy_user_private_key(dummy: "OrgUser", email="dummy@law-orga.de") -> str:
        if settings.TESTING and dummy.email == email:
            u1 = UserKey.create_from_dict(dummy.key)
            u2 = u1.decrypt_self(settings.DUMMY_USER_PASSWORD)
            key = u2.key
            assert isinstance(key, AsymmetricKey)
            return key.get_private_key().decode("utf-8")

        raise ValueError("This method is only available for dummy and in test mode.")

    def __get_user_key_for_test(self) -> UserKey:
        public_key: str = self.key["key"]["public_key"]  # type: ignore
        private_key = Keyring.get_dummy_user_private_key(
            self.user, self.user.user.email
        )
        origin: str = self.key["key"]["origin"]  # type: ignore
        return UserKey(
            AsymmetricKey.create(
                private_key=private_key, origin=origin, public_key=public_key
            )
        )

    def _get_user_key(self) -> UserKey:
        assert self.key is not None

        if settings.TESTING and (
            self.user.user.email == "dummy@law-orga.de"
            or self.user.user.email == "tester@law-orga.de"
        ):
            return self.__get_user_key_for_test()

        return self.__get_user_key_from_session()

    def get_user_key_from_password(self, password: str) -> UserKey:
        user_key = UserKey.create_from_dict(self.key)
        return user_key.decrypt_self(password)

    def get_decryption_key(self, *args, **kwargs) -> AsymmetricKey:
        if self.decryption_key is None:
            key = self._get_user_key()

            assert isinstance(
                key.key, AsymmetricKey
            ), f"key is not an AsymmetricKey it is of type: {type(key.key)}"

            self.decryption_key = key.key

        return self.decryption_key

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union[AsymmetricKey, EncryptedAsymmetricKey]:
        assert self.key is not None
        u = UserKey.create_from_dict(self.key)
        return u.key

    def get_public_key(self) -> bytes:
        return self.get_encryption_key().get_public_key().encode("utf-8")

    def get_private_key(self, *args, **kwargs) -> str:
        return self.get_decryption_key().get_private_key().decode("utf-8")

    def change_password(self, new_password: str) -> UserKey:
        self.load()
        user_key = self._get_user_key()
        new_user_key = user_key.encrypt_self(new_password)
        self.key = new_user_key.as_dict()
        return new_user_key

    def invalidate(self, new_password: str):
        self.load()
        key = AsymmetricKey.generate(AsymmetricEncryptionV1)
        u1 = UserKey(key=key)
        u2 = u1.encrypt_self(new_password)
        self.key = u2.as_dict()
        self.invalidate_group_keys()

    def invalidate_group_keys(self):
        self.load()
        for gkey in self._group_keys:
            gkey.is_invalidated = True

    def test_keys(self):
        self.load()
        for gkey in self._group_keys:
            try:
                gkey._get_decryption_key()
            except DomainError:
                # group key is already invalidated
                continue
            except ValueError:
                gkey.is_invalidated = True
        return not self.has_invalid_keys

    def fix_self(self, other_keyring: "Keyring"):
        self.load()
        other_keyring.load()
        for gkey in self._group_keys:
            if gkey.is_invalidated:
                other_gkey = other_keyring._find_group_key(gkey.group.uuid)
                if other_gkey is not None and not other_gkey.is_invalidated:
                    group_symmetric_key = other_gkey._get_decryption_key()
                    skey_enc = group_symmetric_key.encrypt_self(
                        self.get_encryption_key()
                    )
                    gkey.key = skey_enc.as_dict()
                    gkey.is_invalidated = False

    def _find_group_key(self, group_id: UUID) -> Union["GroupKey", None]:
        self.load()
        for gkey in self._group_keys:
            if gkey.group.uuid == group_id:
                return gkey
        return None

    def get_group_key(self, group_id: UUID) -> SymmetricKey:
        self.load()
        group_key = self._find_group_key(group_id)
        if group_key is None:
            raise KeyNotFoundError("no group key found for the given group id")
        return group_key._get_decryption_key()

    def find_group_key(self, group_id: UUID) -> SymmetricKey | None:
        self.load()
        group_key = self._find_group_key(group_id)
        if group_key is None:
            return None
        return group_key._get_decryption_key()

    def add_group_key(self, group: "Group", by: "OrgUser"):
        self.load()
        key = by.keyring.get_group_key(group.uuid)
        enc_key = key.encrypt_self(self.get_encryption_key())
        group_key = GroupKey(keyring=self, group=group, key=enc_key.as_dict())
        self._group_keys.append(group_key)

    def add_group_key_directly(self, group: "Group", key: SymmetricKey):
        self.load()
        enc_key = key.encrypt_self(self.get_encryption_key())
        group_key = GroupKey(keyring=self, group=group, key=enc_key.as_dict())
        self._group_keys.append(group_key)

    def remove_group_key(self, group: "Group") -> None:
        self.load()
        self._group_keys = list_filter(
            self._group_keys, lambda gkey: gkey.group.uuid != group.uuid
        )


class GroupKey(models.Model):
    keyring: models.ForeignKey["GroupKey", Keyring] = models.ForeignKey(
        Keyring, on_delete=models.CASCADE, related_name="group_keys"
    )
    group: models.ForeignKey["GroupKey", "Group"] = models.ForeignKey(
        "core.Group", on_delete=models.CASCADE, related_name="group_keys"
    )
    key = models.JSONField(null=False, blank=True)
    is_invalidated = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ENC_GroupKey"
        verbose_name_plural = "ENC_GroupKeys"
        unique_together = ("keyring", "group")

    def __str__(self):
        return f"groupKey: {self.keyring.user.email}; group: {self.group.name};"

    def save(self, *args, force=False, **kwargs):
        if force:
            super().save(*args, **kwargs)
            return
        raise Exception("save is disabled use store() of keyring instead")

    def _get_decryption_key(self) -> SymmetricKey:
        if self.is_invalidated:
            raise DomainError("The group key is invalidated.")
        unlock_key = self.keyring.get_decryption_key()
        key = EncryptedSymmetricKey.create_from_dict(self.key)
        return key.decrypt(unlock_key)
