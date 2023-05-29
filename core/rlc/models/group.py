from typing import TYPE_CHECKING

from django.db import models

from core.rlc.models.org import Org
from core.seedwork.domain_layer import DomainError

if TYPE_CHECKING:
    from core.auth.models.org_user import RlcUser


class Group(models.Model):
    @classmethod
    def create(cls, org: Org, name: str, description: str | None, pk=0):
        group = Group(from_rlc=org, name=name)
        group.description = description if description is not None else ""
        if pk:
            group.pk = pk
        return group

    from_rlc = models.ForeignKey(
        Org, related_name="group_from_rlc", on_delete=models.CASCADE, blank=True
    )
    name = models.CharField(max_length=200, null=False)
    visible = models.BooleanField(null=False, default=True)
    members = models.ManyToManyField("RlcUser", related_name="groups", blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return "group: {}; name: {}; rlc: {};".format(
            self.id, self.name, self.from_rlc.name
        )

    @property
    def permissions(self):
        return self.group_has_permission.order_by("permission__name")

    @property
    def member_ids(self) -> list[int]:
        return list(self.members.values_list("id", flat=True))

    def update_information(
        self, name: str | None = None, description: str | None = None
    ):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description

    def has_member(self, user: "RlcUser") -> bool:
        return user.id in self.member_ids

    def add_member(self, new_member: "RlcUser"):
        if new_member.org_id != self.from_rlc_id:
            raise DomainError("The user is not in the same org.")

        if self.has_member(new_member):
            raise DomainError("The user is already a member of this group.")

        self.members.add(new_member)

    def remove_member(self, member: "RlcUser"):
        if not self.has_member(member):
            raise DomainError("The user is not a member of this group.")

        self.members.remove(member)
