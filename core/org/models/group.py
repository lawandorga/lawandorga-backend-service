from typing import TYPE_CHECKING, Union
from uuid import UUID, uuid4

from django.db import models, transaction

from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.org.models.org import Org
from core.seedwork.domain_layer import DomainError

if TYPE_CHECKING:
    from core.auth.models.org_user import OrgUser
    from core.permissions.models import HasPermission


class GroupKey:
    @classmethod
    def generate(cls) -> "GroupKey":
        return cls(SymmetricKey.generate(SymmetricEncryptionV1))

    def __init__(self, key: SymmetricKey):
        self.__key = key

    def get_key(self) -> SymmetricKey:
        return self.__key

    def encrypt(self, owner: "OrgUser") -> "EncryptedGroupKey":
        lock_key = owner.get_encryption_key()
        enc_key = self.__key.encrypt_self(lock_key)
        return EncryptedGroupKey.create(enc_key=enc_key, owner=owner)


class EncryptedGroupKey:
    @classmethod
    def create(
        cls, enc_key: EncryptedSymmetricKey, owner: "OrgUser"
    ) -> "EncryptedGroupKey":
        return cls(enc_key=enc_key, owner_uuid=owner.uuid, is_valid=True)

    @classmethod
    def create_from_dict(cls, data: dict) -> "EncryptedGroupKey":
        assert "enc_key" in data and "owner_uuid" in data, "invalid data dict"

        enc_key = EncryptedSymmetricKey.create_from_dict(data["enc_key"])
        owner_uuid = UUID(data["owner_uuid"])
        is_valid = data.get("is_valid", True)

        return cls(enc_key=enc_key, owner_uuid=owner_uuid, is_valid=is_valid)

    def __init__(
        self, enc_key: EncryptedSymmetricKey, owner_uuid: UUID, is_valid: bool
    ):
        self.__enc_key = enc_key
        self.__owner_uuid = owner_uuid
        self.__is_valid = is_valid

    @property
    def is_valid(self):
        return self.__is_valid

    @property
    def owner_uuid(self):
        return self.__owner_uuid

    def get_key_for_migration(self) -> EncryptedSymmetricKey:
        return self.__enc_key

    def decrypt(self, owner: "OrgUser") -> GroupKey:
        if owner.uuid != self.__owner_uuid:
            raise DomainError("The owner does not match the key.")
        key = self.__enc_key.decrypt(owner.get_decryption_key())
        return GroupKey(key=key)

    def as_dict(self) -> dict:
        return {
            "enc_key": self.__enc_key.as_dict(),
            "owner_uuid": str(self.__owner_uuid),
            "is_valid": self.__is_valid,
        }

    def test(self, owner: "OrgUser") -> bool:
        assert owner.uuid == self.__owner_uuid, "the owner does not match the key"
        assert owner.get_decryption_key(), "owner decryption key can not be fetched"
        try:
            self.decrypt(owner)
        except Exception:
            return False
        return True

    def invalidate_self(self) -> "EncryptedGroupKey":
        return EncryptedGroupKey(
            enc_key=self.__enc_key, owner_uuid=self.__owner_uuid, is_valid=False
        )


class Group(models.Model):
    @classmethod
    def create_simple(cls, org: Org, name: str, description: str | None):
        group = Group(org=org, name=name)
        group.description = description if description is not None else ""
        return group

    @classmethod
    def create(cls, org: Org, name: str, description: str | None, by: "OrgUser"):
        group = Group.create_simple(org=org, name=name, description=description)
        with transaction.atomic():
            group.save()
            group.add_member(by)
            by.keyring.store()
        return group

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    org = models.ForeignKey(
        Org, related_name="groups", on_delete=models.CASCADE, blank=True
    )
    name = models.CharField(max_length=200, null=False)
    visible = models.BooleanField(null=False, default=True)
    members: "models.ManyToManyField[OrgUser, OrgUser]" = models.ManyToManyField(
        "OrgUser", related_name="groups", blank=True
    )
    description = models.TextField(blank=True, null=True)
    keys = models.JSONField(default=list)

    if TYPE_CHECKING:
        group_has_permission: models.QuerySet["HasPermission"]
        # object_keys: models.QuerySet["ObjectKey"]
        org_id: int

    class Meta:
        verbose_name = "ORG_Group"
        verbose_name_plural = "ORG_Groups"

    def __str__(self):
        return "group: {}; name: {}; org: {};".format(self.pk, self.name, self.org.name)

    @property
    def permissions(self):
        return self.group_has_permission.order_by("permission__name")

    @property
    def member_ids(self) -> list[int]:
        return list(self.members.values_list("id", flat=True))

    @property
    def keys_as_model(self) -> list[EncryptedGroupKey]:
        return [EncryptedGroupKey.create_from_dict(key) for key in self.keys]

    def _generate_keys(self, for_member: "OrgUser"):
        assert len(self.keys) == 0, "keys already exist for this group"

        key = GroupKey.generate()
        self.keys = []
        enc_key = key.encrypt(for_member)
        for_member.keyring.load().add_group_key_directly(self, key.get_key())
        self.keys.append(enc_key.as_dict())

    def get_enc_group_key_of_user(self, user: "OrgUser") -> EncryptedGroupKey | None:
        assert len(self.keys), "keys have not been generated for this group"
        assert isinstance(self.keys, list), "keys is not a list"

        for key in self.keys:
            if key["owner_uuid"] == str(user.uuid):
                return EncryptedGroupKey.create_from_dict(key)

        return None

    def invalidate_keys_of(self, user: "OrgUser"):
        assert len(self.keys), "keys have not been generated for this group"
        new_keys = []
        for key in self.keys_as_model:
            if key.owner_uuid == user.uuid:
                new_keys.append(key.invalidate_self().as_dict())
            else:
                new_keys.append(key.as_dict())
        self.keys = new_keys

    def get_encryption_key(self, user: "OrgUser") -> SymmetricKey:
        return user.keyring.get_group_key(self.uuid)

    def get_decryption_key(self, user: "OrgUser") -> SymmetricKey:
        return self.get_encryption_key(user)

    def update_information(
        self, name: str | None = None, description: str | None = None
    ):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description

    def has_member(self, user: "OrgUser") -> bool:
        return user.pk in self.member_ids

    def has_keys(self, user: "OrgUser") -> bool:
        key = self.get_enc_group_key_of_user(user)
        return key is not None

    def has_valid_keys(self, user: "OrgUser") -> bool:
        key = self.get_enc_group_key_of_user(user)
        if key is None:
            return False
        if not key.is_valid:
            return False
        return True

    def fix_keys(self, of: "OrgUser", by: "OrgUser") -> None:
        of.keyring.remove_group_key(self)
        of.keyring.add_group_key(self, by)
        with transaction.atomic():
            of.keyring.store()

    def add_member(self, new_member: "OrgUser", by: Union["OrgUser", None] = None):
        if new_member.org_id != self.org.pk:
            raise DomainError("The user is not in the same org.")

        if self.has_member(new_member):
            raise DomainError("The user is already a member of this group.")

        if len(self.keys):
            assert by is not None, "by must be set if keys exist"
            new_member.keyring.add_group_key(self, by=by)
        else:
            self._generate_keys(new_member)

        with transaction.atomic():
            self.save()
            self.members.add(new_member)
            new_member.keyring.store()

    def remove_member(self, member: "OrgUser"):
        if not self.has_member(member):
            raise DomainError("The user is not a member of this group.")

        member.keyring.remove_group_key(self)

        with transaction.atomic():
            self.save()
            self.members.remove(member)
            member.keyring.store()
