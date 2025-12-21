from datetime import timedelta
from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models
from django.utils import timezone
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


class Keyring(models.Model):
    user: models.OneToOneField["Keyring", OrgUser] = models.OneToOneField(
        OrgUser, on_delete=models.CASCADE, related_name="keyring"
    )
    key = models.JSONField(null=False, blank=True)

    if TYPE_CHECKING:
        object_keys: models.QuerySet["ObjectKey"]

    def __get_session(self) -> CustomSession:
        memory_cache_session_key = "session-of-org-user-{}".format(self.pk)
        memory_cache_time_key = "time-of-org-user-{}".format(self.pk)

        if hasattr(self.__class__, memory_cache_session_key) and hasattr(
            self.__class__, memory_cache_time_key
        ):
            if timezone.now() < getattr(self.__class__, memory_cache_time_key):
                return getattr(self.__class__, memory_cache_session_key)
            else:
                delattr(self.__class__, memory_cache_time_key)
                delattr(self.__class__, memory_cache_session_key)

        session = (
            CustomSession.objects.filter(user_id=self.user.user_id)
            .order_by("-expire_date")
            .first()
        )

        if session is None:
            raise Exception(
                f"No session found for user '{self.user.user_id}' with last login '{self.user.user.last_login}'"
            )

        setattr(
            self.__class__,
            memory_cache_time_key,
            timezone.now() + timedelta(seconds=10),
        )
        setattr(self.__class__, memory_cache_session_key, session)

        return session

    def _get_user_key(self) -> UserKey:
        assert self.key is not None

        if settings.TESTING and (
            self.user.user.email == "dummy@law-orga.de"
            or self.user.user.email == "tester@law-orga.de"
        ):
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

        session = self.__get_session()
        decoded = session.get_decoded()
        key = UserKey.create_from_unsafe_dict(decoded["user_key"])
        return key

    def get_public_key(self) -> bytes:
        return self.__get_encryption_key().get_public_key().encode("utf-8")

    def get_private_key(self, *args, **kwargs) -> str:
        return self.__get_decryption_key().get_private_key().decode("utf-8")

    def __get_decryption_key(self, *args, **kwargs) -> AsymmetricKey:
        key = self._get_user_key()

        assert isinstance(
            key.key, AsymmetricKey
        ), f"key is not an AsymmetricKey it is of type: {type(key.key)}"
        return key.key

    def __get_encryption_key(
        self, *args, **kwargs
    ) -> Union[AsymmetricKey, EncryptedAsymmetricKey]:
        assert self.key is not None
        u = UserKey.create_from_dict(self.key)
        return u.key

    def get_object_key(self, object_id: UUID, object_type: str) -> SymmetricKey:
        keys = self.object_keys.all()
        for key in keys:
            if key.object_id == object_id and key.object_type == object_type:
                return key.get_decryption_key(self.__get_decryption_key())
        raise ValueError("No object key found for the given object id and type.")

    def add_object_key(
        self, object_id: UUID, object_type: str, key: SymmetricKey
    ) -> "ObjectKey":
        enc_key = key.encrypt_self(self.__get_encryption_key())
        return ObjectKey(
            keyring=self,
            object_id=object_id,
            object_type=object_type,
            key=enc_key.as_dict(),
        )


class ObjectKey(models.Model):
    keyring: models.ForeignKey["ObjectKey", Keyring] = models.ForeignKey(
        Keyring, on_delete=models.CASCADE, related_name="object_keys"
    )
    object_id = models.UUIDField(null=False, blank=False)
    object_type = models.CharField(max_length=100, null=False, blank=False)
    key = models.JSONField(null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("keyring", "object_id", "object_type")

    def get_decryption_key(self, unlock_key: AsymmetricKey) -> SymmetricKey:
        key = EncryptedSymmetricKey.create_from_dict(self.key)
        return key.decrypt(unlock_key)
