from uuid import uuid4

from django.db import models

from core.auth.models.org_user import OrgUser
from core.rlc.models.org import Org


class Letterhead(models.Model):
    @classmethod
    def create(
        cls,
        user: OrgUser,
        name: str,
        description: str,
        address_line_1: str,
        address_line_2: str,
        address_line_3: str,
        address_line_4: str,
        address_line_5: str,
        text_right: str,
    ):
        return cls(
            org_id=user.org_id,
            name=name,
            description=description,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            address_line_3=address_line_3,
            address_line_4=address_line_4,
            address_line_5=address_line_5,
            text_right=text_right,
        )

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="letterheads")
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    uuid = models.UUIDField(unique=True, default=uuid4)
    address_line_1 = models.CharField(max_length=256)
    address_line_2 = models.CharField(max_length=256, blank=True)
    address_line_3 = models.CharField(max_length=256, blank=True)
    address_line_4 = models.CharField(max_length=256, blank=True)
    address_line_5 = models.CharField(max_length=256, blank=True)
    logo = models.ImageField(upload_to="letterheads", blank=True)

    text_right = models.TextField(blank=True)

    class Meta:
        verbose_name = "Letterhead"
        verbose_name_plural = "Letterheads"

    @property
    def template_type(self):
        return "letterhead"

    def update_meta(self, name: str, description: str):
        self.name = name
        self.description = description

    def update_text(
        self,
        address_line_1: str,
        address_line_2: str,
        address_line_3: str,
        address_line_4: str,
        address_line_5: str,
        text_right: str,
    ):
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.address_line_3 = address_line_3
        self.address_line_4 = address_line_4
        self.address_line_5 = address_line_5
        self.text_right = text_right
