from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from django.db import models

from core.auth.models.org_user import OrgUser
from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead
from core.rlc.models.org import Org


class Template(models.Model):
    @classmethod
    def create(
        cls,
        user: OrgUser,
        name: str,
        description: str,
        type: Literal["letterhead", "footer"],
    ) -> tuple["Template", Footer | Letterhead]:
        template = cls(
            org_id=user.org_id,
            name=name,
            description=description,
        )
        if type == "letterhead":
            content = template.add_letterhead()
        else:
            content = template.add_footer()
        return template, content

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="templates")
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    uuid = models.UUIDField(unique=True, default=uuid4)
    letterhead = models.OneToOneField(Letterhead, on_delete=models.SET_NULL, null=True)
    footer = models.OneToOneField(Footer, on_delete=models.SET_NULL, null=True)

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        constraints = [
            models.CheckConstraint(
                check=models.Q(letterhead__isnull=False)
                | models.Q(footer__isnull=False),
                name="either_letterhead_or_footer",
            )
        ]

    def add_letterhead(self):
        lh = Letterhead.create(self.org_id, "", "", "", "", "", "", "", "")
        self.letterhead = lh
        return lh

    def add_footer(self):
        footer = Footer.create(self.org_id, "", "", "", "", "", "")
        self.footer = footer
        return footer

    def update_name(self, name: str | None):
        if name:
            self.name = name

    def update_description(self, description: str | None):
        if description:
            self.description = description

    def update_letterhead(self, letterhead: Letterhead):
        self.letterhead = letterhead

    def update_footer(self, footer: Footer):
        self.footer = footer
