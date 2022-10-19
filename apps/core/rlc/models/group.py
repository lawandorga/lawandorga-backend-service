from typing import TYPE_CHECKING

from django.db import models

from apps.core.rlc.models.org import Org
from apps.static.domain_layer import DomainError

if TYPE_CHECKING:
    from apps.core.auth.models.org_user import RlcUser


class Group(models.Model):
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

    def add_member(self, new_member: "RlcUser"):
        if new_member.org_id != self.from_rlc_id:
            raise DomainError("The user is not in the same org.")

        if self.members.filter(id=new_member.id).exists():
            raise DomainError("The user is already a member of this group.")

        self.members.add(new_member)
        self.save()

    def remove_member(self, member: "RlcUser"):
        if not self.members.filter(id=member.id).exists():
            raise DomainError("The user is not a member of this group.")

        self.members.remove(member)
        self.save()
