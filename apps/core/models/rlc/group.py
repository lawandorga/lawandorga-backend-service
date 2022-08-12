from django.db import models

from apps.core.models.rlc.rlc import Rlc
from apps.core.models.auth.user import UserProfile


class Group(models.Model):
    from_rlc = models.ForeignKey(
        Rlc, related_name="group_from_rlc", on_delete=models.CASCADE, blank=True
    )
    name = models.CharField(max_length=200, null=False)
    visible = models.BooleanField(null=False, default=True)
    group_members = models.ManyToManyField(
        UserProfile, related_name="rlcgroups", blank=True
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return "group: {}; name: {}; rlc: {};".format(
            self.id, self.name, self.from_rlc.name
        )
