from typing import TYPE_CHECKING
from uuid import UUID

from django.db import models

from core.auth.models.org_user import OrgUser
from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead
from core.org.models.org import Org


class Template(models.Model):
    @classmethod
    def create(
        cls,
        user: OrgUser,
        uuid: UUID,
        name: str,
        description: str,
    ) -> "Template":
        template = cls(
            uuid=uuid,
            org_id=user.org_id,
            name=name,
            description=description,
        )
        return template

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="templates")
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    uuid = models.UUIDField(unique=True)
    letterhead = models.OneToOneField(Letterhead, on_delete=models.SET_NULL, null=True)
    footer = models.OneToOneField(Footer, on_delete=models.SET_NULL, null=True)

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "COL_Template"
        verbose_name_plural = "COL_Templates"

    def __str__(self) -> str:
        return self.name

    def update_name(self, name: str):
        self.name = name

    def update_description(self, description: str):
        self.description = description

    def update_letterhead(self, letterhead: Letterhead):
        self.letterhead = letterhead
        self.save()

    def update_footer(self, footer: Footer):
        self.footer = footer
        self.save()
