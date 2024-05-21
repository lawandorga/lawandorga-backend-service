# 4 einfache textfelder - CHECK
# spalte 1, spalte 2, spalte 3, spalte 4 - CHECK
# verbunden mit org - CHECK
# uuid field - CHECK
from uuid import uuid4

from django.db import models

from core.auth.models.org_user import OrgUser
from core.rlc.models.org import Org


class Footer(models.Model):
    @classmethod
    def create(
        cls,
        user: OrgUser,
        column_1: str,
        column_2: str,
        column_3: str,
        column_4: str,
    ):
        return cls(
            org_id=user.org_id,
            column_1=column_1,
            column_2=column_2,
            column_3=column_3,
            column_4=column_4,
        )

    uuid = models.UUIDField(unique=True, default=uuid4)
    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="footers")
    column_1 = models.TextField(max_length=256, blank=True)
    column_2 = models.TextField(max_length=256, blank=True)
    column_3 = models.TextField(max_length=256, blank=True)
    column_4 = models.TextField(max_length=256, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footers"

    @property
    def template_type(self):
        return "Footer"

    def update_text(self, column_1: str, column_2: str, column_3: str, column_4: str):
        self.column_1 = column_1
        self.column_2 = column_2
        self.column_3 = column_3
        self.column_4 = column_4
