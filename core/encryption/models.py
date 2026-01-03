from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models, transaction
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

from seedwork.functional import list_filter, list_find, list_map


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
    # TODO: UserKey has to be in a special state here (encrypted or not) please check later
    @classmethod
    def create(cls, user: OrgUser | None, key: UserKey) -> "Keyring":
        keyring = Keyring()
        if user is not None:
            keyring = Keyring(user=user)
        keyring.key = key.as_dict()
        keyring._object_keys = []
        keyring._group_keys = []
        keyring._is_loaded = True
        return keyring

    user: models.OneToOneField["Keyring", OrgUser] = models.OneToOneField(
        OrgUser, on_delete=models.CASCADE, related_name="keyring"
    )
    key = models.JSONField(null=False, blank=True)
    decryption_key: AsymmetricKey | None = None

    objects = KeyringManager()

    if TYPE_CHECKING:
        _object_keys: list["ObjectKey"]
        _group_keys: list["GroupKey"]
        _group_object_keys: list["ObjectKey"]
        object_keys: models.QuerySet["ObjectKey"]
        group_keys: models.QuerySet["GroupKey"]

    class Meta:
        verbose_name = "ENC_Keyring"
        verbose_name_plural = "ENC_Keyrings"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_loaded = False
        self._added_group_object_keys = []
        self._removed_group_object_keys = []

    def __str__(self):
        if not hasattr(self, "user"):
            return "keyring: None;"
        return f"keyring: {self.user.email};"

    def __repr__(self):
        return self.__str__()

    def load(self, force: bool = False) -> "Keyring":
        if self._is_loaded and not force:
            return self
        self._object_keys = list(self.object_keys.all())
        self._group_keys = list(self.group_keys.all())
        for gkey in self._group_keys:
            gkey.load()
        self._is_loaded = True
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
        with transaction.atomic():
            super().save()
            self.object_keys.all().delete()
            ObjectKey.objects.bulk_create(self._object_keys)
            self.group_keys.all().delete()
            GroupKey.objects.bulk_create(self._group_keys)
            ObjectKey.objects.exclude(group=None).all()
            ObjectKey.objects.filter(
                pk__in=list_map(self._removed_group_object_keys, lambda k: k.pk)
            ).delete()
            ObjectKey.objects.bulk_create(self._added_group_object_keys)
        self._removed_group_object_keys = []
        self._added_group_object_keys = []

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

    def _find_group_key(self, group_id: UUID) -> "GroupKey":
        self.load()
        for gkey in self._group_keys:
            if gkey.group.uuid == group_id:
                return gkey
        raise KeyNotFoundError("no group key found for the given group id")

    def get_group_key(self, group_id: UUID) -> SymmetricKey:
        self.load()
        group_key = self._find_group_key(group_id)
        return group_key._get_decryption_key()

    def add_group_key(self, group: Group, by: "OrgUser"):
        self.load()
        key = by.keyring.get_group_key(group.uuid)
        enc_key = key.encrypt_self(self._get_encryption_key())
        group_key = GroupKey(keyring=self, group=group, key=enc_key.as_dict())
        group_key._object_keys = []
        self._group_keys.append(group_key)

    def add_group_key_directly(self, group: Group, key: SymmetricKey):
        self.load()
        enc_key = key.encrypt_self(self._get_encryption_key())
        group_key = GroupKey(keyring=self, group=group, key=enc_key.as_dict())
        group_key._object_keys = []
        self._group_keys.append(group_key)

    def remove_group_key(self, group: Group) -> None:
        self.load()
        self._group_keys = list_filter(
            self._group_keys, lambda gkey: gkey.group.uuid != group.uuid
        )

    def get_object_key(self, object_id: UUID, object_type: ObjectTypes) -> SymmetricKey:
        self.load()
        for key in self._object_keys:
            if key.object_id == object_id and key.object_type == object_type.value:
                return key._get_decryption_key(self._get_decryption_key())
        for gkey in self._group_keys:
            for key in gkey._object_keys:
                if key.object_id == object_id and key.object_type == object_type.value:
                    return key._get_decryption_key(gkey._get_decryption_key())
        raise KeyNotFoundError("no object key found for the given object id and type")

    def has_object_key(self, object_id: UUID, object_type: ObjectTypes) -> bool:
        self.load()
        for key in self._object_keys:
            if key.object_id == object_id and key.object_type == object_type.value:
                return True
        for gkey in self._group_keys:
            for key in gkey._object_keys:
                if key.object_id == object_id and key.object_type == object_type.value:
                    return True
        return False

    def add_object_key(
        self, object_id: UUID, object_type: ObjectTypes, key: SymmetricKey
    ):
        self.load()
        enc_key = key.encrypt_self(self._get_encryption_key())
        obj_key = ObjectKey(
            keyring=self,
            object_id=object_id,
            object_type=object_type.value,
            key=enc_key.as_dict(),
        )
        self._object_keys.append(obj_key)

    def add_object_key_for_group(
        self, group: Group, object_id: UUID, object_type: ObjectTypes
    ):
        self.load()
        for gkey in self._group_keys:
            if gkey.group.uuid == group.uuid:
                group_key = gkey
        assert group_key is not None, "group key must be found"
        key = self.get_object_key(object_id=object_id, object_type=object_type)
        enc_key = key.encrypt_self(group.get_encryption_key(self.user))
        obj_key = ObjectKey(
            group=group,
            object_id=object_id,
            object_type=object_type.value,
            key=enc_key.as_dict(),
        )
        group_key._object_keys.append(obj_key)
        self._added_group_object_keys.append(obj_key)

    def remove_object_key(self, object_id: UUID, object_type: ObjectTypes):
        self.load()
        self._object_keys = list_filter(
            self._object_keys,
            lambda key: not (
                key.object_id == object_id and key.object_type == object_type.value
            ),
        )

    def remove_object_key_for_group(
        self, group: Group, object_id: UUID, object_type: ObjectTypes
    ):
        self.load()
        group_key = self._find_group_key(group.uuid)
        group_object_key = list_find(
            group_key._object_keys,
            lambda key: key.object_id == object_id
            and key.object_type == object_type.value,
        )
        assert group_object_key is not None, "group object key must be found"
        group_key._object_keys.remove(group_object_key)
        self._removed_group_object_keys.append(group_object_key)


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
        _object_keys: list["ObjectKey"]

    class Meta:
        verbose_name = "ENC_GroupKey"
        verbose_name_plural = "ENC_GroupKeys"
        unique_together = ("keyring", "group")

    def __str__(self):
        return f"groupKey: {self.keyring.user.email}; group: {self.group.name};"

    def save(self, *args, **kwargs):
        raise Exception("save is disabled use store() of keyring instead")

    def load(self):
        self._object_keys = list(self.group.object_keys.all())

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
        return f"{start} object_type: {self.object_type}; object_id: {self.object_id}; pk: {self.pk};"

    def save(self, *args, **kwargs):
        raise Exception("save is disabled use store() of keyring instead")

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
