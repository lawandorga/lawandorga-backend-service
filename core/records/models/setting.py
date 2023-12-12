from typing import Optional
from uuid import uuid4

from django.db import models
from django.db.models import Q

from core.auth.models import OrgUser
from core.rlc.models.org import Org


class RecordsView(models.Model):
    @classmethod
    def create(
        cls, name: str, user: OrgUser, columns=list[str], shared=False, pk=0
    ) -> "RecordsView":
        view = RecordsView(name=name, columns=columns)
        if shared is True:
            view.org = user.org
        else:
            view.user = user
        if pk:
            view.pk = pk
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

    class Meta:
        verbose_name = "Records-View"
        verbose_name_plural = "Records-Views"
        ordering = ["-org", "ordering"]
        constraints = [
            models.CheckConstraint(
                check=(Q(org__isnull=True) & Q(user__isnull=False))
                | (Q(org__isnull=False) & Q(user__isnull=True)),
                name="records_view_one_of_both_is_set",
            )
        ]

    def __str__(self):
        return "recordsView: {}; of: {};".format(
            self.uuid, self.user.email if self.user else self.org.name
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
