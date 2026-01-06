from typing import TYPE_CHECKING, Union
from uuid import uuid4

from django.db import models, transaction

from core.encryption.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.encryption.value_objects.symmetric_key import (
    SymmetricKey,
)
from core.org.models.org import Org
from core.seedwork.domain_layer import DomainError

if TYPE_CHECKING:
    from core.auth.models.org_user import OrgUser
    from core.permissions.models import HasPermission


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
    members: "models.ManyToManyField[OrgUser, Group]" = models.ManyToManyField(
        "OrgUser", related_name="groups", blank=True
    )
    description = models.TextField(blank=True, null=True)
    keys = models.JSONField(default=list)

    if TYPE_CHECKING:
        group_has_permission: models.QuerySet["HasPermission"]
        org_id: int

    class Meta:
        verbose_name = "ORG_Group"
        verbose_name_plural = "ORG_Groups"

    def __str__(self):
        return "group: {}; name: {}; org: {};".format(self.pk, self.name, self.org.name)

    @property
    def permissions(self):
        return self.group_has_permission.order_by("permission__name")

    def _generate_keys(self, for_member: "OrgUser"):
        from core.encryption.models import GroupKey

        assert (
            GroupKey.objects.filter(group=self).count() == 0
        ), "keys already exist for this group"

        key = SymmetricKey.generate(SymmetricEncryptionV1)
        for_member.keyring.load().add_group_key_directly(self, key)

    def update_information(
        self, name: str | None = None, description: str | None = None
    ):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description

    def has_member(self, user: "OrgUser") -> bool:
        return self.members.contains(user)

    def add_member(self, new_member: "OrgUser", by: Union["OrgUser", None] = None):
        from core.encryption.models import GroupKey

        if new_member.org_id != self.org.pk:
            raise DomainError("The user is not in the same org.")

        if self.has_member(new_member):
            raise DomainError("The user is already a member of this group.")

        if GroupKey.objects.filter(group=self).exists():
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
