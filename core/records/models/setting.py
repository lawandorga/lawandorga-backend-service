from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from django.db import models

from core.auth.models import OrgUser
from core.org.models.org import Org
from core.seedwork.domain_layer import DomainError


class RecordsView(models.Model):
    @classmethod
    def create(
        cls,
        name: str,
        user: OrgUser,
        columns: list[str],
        shared=False,
        pk=0,
        ordering=0,
    ) -> "RecordsView":
        view = RecordsView(name=name, columns=columns)
        if shared is True:
            view.org = user.org
        view.user = user
        if pk:
            view.pk = pk
        view.ordering = ordering
        return view

    name = models.CharField(max_length=200)
    org = models.ForeignKey(
        Org,
        related_name="records_views",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        OrgUser,
        related_name="records_views",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    columns = models.JSONField()
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid4)
    ordering = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        user: models.ForeignKey[OrgUser] | None  # type: ignore[no-redef]

    class Meta:
        verbose_name = "REC_RecordsView"
        verbose_name_plural = "REC_RecordsViews"
        ordering = ["ordering"]

    def __str__(self):
        return "recordsView: {}; of: {};".format(
            self.uuid,
            self.user.email if self.user else self.org.name if self.org else "None",
        )

    @property
    def shared(self):
        return self.org is not None

    def update_information(
        self, name: Optional[str], columns: Optional[list[str]], ordering: int
    ):
        if name is not None:
            self.name = name
        if columns is not None:
            self.columns = columns
        if ordering is not None:
            self.ordering = ordering

    def make_shared(self, user: OrgUser):
        if self.shared:
            raise DomainError("This view is already shared.")
        self.org = user.org

    def make_private(self, actor: OrgUser):
        if not self.shared:
            raise DomainError("This view is already private.")
        if self.user and self.user != actor:
            raise DomainError(
                "You can not make this view private, because you are not the creator of it."
            )
        self.org = None
        self.user = actor
