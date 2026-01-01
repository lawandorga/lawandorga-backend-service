from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models
from git import TYPE_CHECKING

from core.auth.domain.user_key import UserKey
from core.auth.models import OrgUser
from core.auth.models.session import CustomSession
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.org.models.group import Group


class KeyringManager(models.Manager["Keyring"]):
    def load(self, user: OrgUser) -> "Keyring":
        keyring = (
            self.filter(user=user)
            .prefetch_related("object_keys", "group_keys", "group_keys__object_keys")
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

    def get_object_key(self, object_id: UUID, object_type: str) -> SymmetricKey:
        for key in self.object_keys.all():
            if key.object_id == object_id and key.object_type == object_type:
                return key._get_decryption_key(self._get_decryption_key())
        for gkey in self.group_keys.all():
            for key in gkey.object_keys.all():
                if key.object_id == object_id and key.object_type == object_type:
                    return key._get_decryption_key(gkey._get_decryption_key())
        raise ValueError("no object key found for the given object id and type.")

    def add_object_key(
        self, object_id: UUID, object_type: str, key: SymmetricKey
    ) -> "ObjectKey":
        enc_key = key.encrypt_self(self._get_encryption_key())
        return ObjectKey(
            keyring=self,
            object_id=object_id,
            object_type=object_type,
            key=enc_key.as_dict(),
        )


class GroupKey(models.Model):
    keyring: models.ForeignKey["GroupKey", Keyring] = models.ForeignKey(
        Keyring, on_delete=models.CASCADE, related_name="group_keys"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_keys"
    )
    key = models.JSONField(null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        object_keys: models.QuerySet["ObjectKey"]

    class Meta:
        unique_together = ("keyring", "group")

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
    group = models.ForeignKey(
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
