from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models
from git import TYPE_CHECKING

from core.auth.domain.user_key import UserKey
from core.auth.models import OrgUser
from core.auth.models.session import CustomSession
from core.encryption.types import ObjectTypes
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
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
        return keyring


class Keyring(models.Model):
    user: models.OneToOneField["Keyring", OrgUser] = models.OneToOneField(
        OrgUser, on_delete=models.CASCADE, related_name="keyring"
    )
    key = models.JSONField(null=False, blank=True)
    decryption_key: AsymmetricKey | None = None

    objects = KeyringManager()

    if TYPE_CHECKING:
        object_keys: models.QuerySet["ObjectKey"]
        group_keys: models.QuerySet["GroupKey"]

    class Meta:
        verbose_name = "ENC_Keyring"
        verbose_name_plural = "ENC_Keyrings"

    def __str__(self):
        return f"keyring: {self.user.email};"

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

    def __get_user_key_for_test(self) -> UserKey:
        public_key: str = self.key["key"]["public_key"]  # type: ignore
        private_key = OrgUser.get_dummy_user_private_key(
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

    def _get_decryption_key(self, *args, **kwargs) -> AsymmetricKey:
        if self.decryption_key is None:
            key = self._get_user_key()

            assert isinstance(
                key.key, AsymmetricKey
            ), f"key is not an AsymmetricKey it is of type: {type(key.key)}"

            self.decryption_key = key.key

        return self.decryption_key

    def _get_encryption_key(
        self, *args, **kwargs
    ) -> Union[AsymmetricKey, EncryptedAsymmetricKey]:
        assert self.key is not None
        u = UserKey.create_from_dict(self.key)
        return u.key

    def get_public_key(self) -> bytes:
        return self._get_encryption_key().get_public_key().encode("utf-8")

    def get_private_key(self, *args, **kwargs) -> str:
        return self._get_decryption_key().get_private_key().decode("utf-8")

    def get_group_key(self, group_id: UUID) -> SymmetricKey:
        for gkey in self.group_keys.all():
            if gkey.group.uuid == group_id:
                return gkey._get_decryption_key()
        raise KeyNotFoundError("no group key found for the given group id")

    def add_group_key(self, group: Group, by: "OrgUser") -> "GroupKey":
        key = by.keyring.get_group_key(group.uuid)
        enc_key = key.encrypt_self(self._get_encryption_key())
        group_key = GroupKey(keyring=self, group=group, key=enc_key.as_dict())
        group_key.save()
        return group_key

    def add_group_key_directly(self, group: Group, key: SymmetricKey) -> "GroupKey":
        enc_key = key.encrypt_self(self._get_encryption_key())
        group_key = GroupKey(keyring=self, group=group, key=enc_key.as_dict())
        group_key.save()
        return group_key

    def remove_group_key(self, group: Group) -> None:
        for gkey in self.group_keys.all():
            if gkey.group.uuid == group.uuid:
                gkey.delete()

    def get_object_key(self, object_id: UUID, object_type: ObjectTypes) -> SymmetricKey:
        for key in self.object_keys.all():
            if key.object_id == object_id and key.object_type == object_type.value:
                return key._get_decryption_key(self._get_decryption_key())
        for gkey in self.group_keys.all():
            for key in gkey.group.object_keys.all():
                if key.object_id == object_id and key.object_type == object_type.value:
                    return key._get_decryption_key(gkey._get_decryption_key())
        raise KeyNotFoundError("no object key found for the given object id and type")

    def add_object_key(
        self, object_id: UUID, object_type: ObjectTypes, key: SymmetricKey
    ) -> "ObjectKey":
        enc_key = key.encrypt_self(self._get_encryption_key())
        obj_key = ObjectKey(
            keyring=self,
            object_id=object_id,
            object_type=object_type.value,
            key=enc_key.as_dict(),
        )
        obj_key.save()
        return obj_key

    def add_object_key_for_group(
        self, group: Group, object_id: UUID, object_type: ObjectTypes
    ) -> "ObjectKey":
        key = self.get_object_key(object_id=object_id, object_type=object_type)
        enc_key = key.encrypt_self(group.get_encryption_key(self.user))
        obj_key = ObjectKey(
            group=group,
            object_id=object_id,
            object_type=object_type.value,
            key=enc_key.as_dict(),
        )
        obj_key.save()
        return obj_key

    def remove_object_key(self, object_id: UUID, object_type: ObjectTypes) -> None:
        for key in self.object_keys.all():
            if key.object_id == object_id and key.object_type == object_type.value:
                key.delete()

    @staticmethod
    def remove_object_key_for_group(
        group: Group, object_id: UUID, object_type: ObjectTypes
    ) -> None:
        for key in group.object_keys.all():
            if key.object_id == object_id and key.object_type == object_type.value:
                key.delete()


class GroupKey(models.Model):
    keyring: models.ForeignKey["GroupKey", Keyring] = models.ForeignKey(
        Keyring, on_delete=models.CASCADE, related_name="group_keys"
    )
    group: models.ForeignKey["GroupKey", Group] = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_keys"
    )
    key = models.JSONField(null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        object_keys: models.QuerySet["ObjectKey"]

    class Meta:
        verbose_name = "ENC_GroupKey"
        verbose_name_plural = "ENC_GroupKeys"
        unique_together = ("keyring", "group")

    def __str__(self):
        return f"groupKey: {self.keyring.user.email}; group: {self.group.name};"

    def _get_decryption_key(self) -> SymmetricKey:
        unlock_key = self.keyring._get_decryption_key()
        key = EncryptedSymmetricKey.create_from_dict(self.key)
        return key.decrypt(unlock_key)


class ObjectKey(models.Model):
    keyring: models.ForeignKey["ObjectKey", Keyring | None] = models.ForeignKey(
        Keyring,
        on_delete=models.CASCADE,
        related_name="object_keys",
        null=True,
        blank=True,
    )
    group: models.ForeignKey["ObjectKey", Group | None] = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="object_keys",
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=False, blank=False)
    object_type = models.CharField(max_length=100, null=False, blank=False)
    key = models.JSONField(null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ENC_ObjectKey"
        verbose_name_plural = "ENC_ObjectKeys"
        unique_together = ("keyring", "object_id", "object_type")
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(keyring__isnull=False) & models.Q(group__isnull=True)
                )
                | (models.Q(keyring__isnull=True) & models.Q(group__isnull=False)),
                name="one_of_both_is_set_object_key",
            )
        ]

    def __str__(self):
        if self.keyring is not None:
            start = f"objectKey: {self.keyring.user.email};"
        else:
            assert self.group is not None
            start = f"objectKey: {self.group.name};"
        return f"{start} object_type: {self.object_type}; object_id: {self.object_id};"

    def _get_decryption_key(
        self, unlock_key: AsymmetricKey | SymmetricKey
    ) -> SymmetricKey:
        """
        Decrypts the encrypted symmetric key for this object.
        The key used for decryption (unlock_key) is:
        a) The user's private key if the keyring is set (object key belongs directly to a user).
        b) The symmetric group key if this object key belongs to a group (object key is part of a group).
        """
        key = EncryptedSymmetricKey.create_from_dict(self.key)
        return key.decrypt(unlock_key)
