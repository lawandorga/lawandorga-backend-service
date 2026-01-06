from typing import TYPE_CHECKING

from django.db import models
from tinymce import models as tinymce_models

if TYPE_CHECKING:
    from core.auth.models import OrgUser


class LegalRequirement(models.Model):
    title = models.CharField(max_length=1000)
    content = tinymce_models.HTMLField()
    accept_required = models.BooleanField()
    show_on_register = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    button_text = models.CharField(default="Accept", max_length=1000)
    accept_text = models.CharField(default="Accepted", max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        events: models.QuerySet["LegalRequirementEvent"]

    def __str__(self):
        return "legalRequirement: {}; title: {};".format(self.pk, self.title)

    class Meta:
        ordering = ["order"]
        verbose_name = "LEG_LegalRequirement"
        verbose_name_plural = "LEG_LegalRequirements"

    @classmethod
    def is_locked(cls, user: "OrgUser") -> bool:
        lrs = LegalRequirement.objects.filter(accept_required=True)
        lrs_list = list(lrs)
        for lr in lrs_list:
            if not lr.is_accepted(user):
                return True
        return False

    def is_accepted(self, user: "OrgUser") -> bool:
        event = self.events.filter(user=user).order_by("-created").last()
        if event:
            return event.accepted
        return False

    def _set_accepted_of_user(self, user: "OrgUser"):
        if (
            hasattr(self, "events_of_user")
            and len(self.events_of_user)
            and self.events_of_user[-1].accepted
        ):
            self.accepted_of_user = True
        else:
            self.accepted_of_user = False

    def _set_events_of_user(self, user: OrgUser):
        self.events_of_user = list(self.events.filter(user=user).order_by("-created"))


class LegalRequirementEvent(models.Model):
    legal_requirement = models.ForeignKey(
        LegalRequirement,
        on_delete=models.CASCADE,
        related_name="events",
    )
    user = models.ForeignKey(
        "core.OrgUser",
        on_delete=models.CASCADE,
        related_name="legal_requirement_events",
    )
    actor = models.CharField(max_length=1000, blank=True)
    text = models.TextField(blank=True)
    accepted = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "event: {}; legalRequirement: {};".format(
            self.pk, self.legal_requirement.title
        )

    class Meta:
        verbose_name = "LEG_LegalRequirementEvent"
        verbose_name_plural = "LEG_LegalRequirementEvents"
