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
        # TODO: Possibly letterhead plus footer | None
    ):
        return cls(
            org_id=user.org_id,
            name=name,
            description=description,
        )

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="templates")
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    uuid = models.UUIDField(unique=True, default=uuid4)
    letterhead = models.ForeignKey(Letterhead, on_delete=models.SET_NULL, null=True)
    footer = models.ForeignKey(Footer, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"

    def update_name(self, name: str):
        self.name = name

    def update_description(self, description: str):
        self.description = description

    def update_letterhead(self, letterhead: Letterhead):
        self.letterhead = letterhead

    def update_footer(self, footer: Footer):
        self.footer = footer
