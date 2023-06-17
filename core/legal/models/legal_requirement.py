from typing import TYPE_CHECKING

from django.db import models
from tinymce import models as tinymce_models

from core.auth.models import RlcUser

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class LegalRequirement(models.Model):
    title = models.CharField(max_length=1000)
    content = tinymce_models.HTMLField()
    accept_required = models.BooleanField()
    show_on_register = models.BooleanField(default=False)
    rlc_users = models.ManyToManyField(
        RlcUser, through="LegalRequirementUser", related_name="legal_requirements"
    )
    order = models.IntegerField(default=0)
    button_text = models.CharField(default="Accept", max_length=1000)
    accept_text = models.CharField(default="Accepted", max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        events: RelatedManager["LegalRequirementEvent"]

    def __str__(self):
        return "legalRequirement: {}; title: {};".format(self.id, self.title)

    class Meta:
        ordering = ["order"]
        verbose_name = "LegalRequirement"
        verbose_name_plural = "LegalRequirements"

    def _set_accepted_of_user(self, user: RlcUser):
        if (
            hasattr(self, "events_of_user")
            and len(self.events_of_user)
            and self.events_of_user[-1].accepted
        ):
            self.accepted_of_user = True
        else:
            self.accepted_of_user = False

    def _set_events_of_user(self, user: RlcUser):
        self.events_of_user = list(self.events.filter(user=user).order_by("-created"))


class LegalRequirementUser(models.Model):
    legal_requirement = models.ForeignKey(
        LegalRequirement,
        on_delete=models.CASCADE,
        related_name="legal_requirements_user",
    )
    rlc_user = models.ForeignKey(
        RlcUser, on_delete=models.CASCADE, related_name="legal_requirements_user"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "legalRequirementUser: {}; legalRequirement: {}; user: {};".format(
            self.id, self.legal_requirement.title, self.rlc_user.id
        )

    class Meta:
        verbose_name = "LegalRequirementUser"
        verbose_name_plural = "LegalRequirementUsers"
        unique_together = ["legal_requirement", "rlc_user"]
        ordering = ["legal_requirement__order"]

    @property
    def accepted(self):
        last_event = self.events.order_by("created").last()
        if last_event:
            return last_event.accepted
        return False

    @property
    def events_list(self):
        events = list(self.events.order_by("created"))
        return events


class LegalRequirementEvent(models.Model):
    legal_requirement_user = models.ForeignKey(
        LegalRequirementUser,
        on_delete=models.CASCADE,
        related_name="events",
        blank=True,
        null=True,
    )
    legal_requirement = models.ForeignKey(
        LegalRequirement,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="events",
    )
    user = models.ForeignKey(
        RlcUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="legal_requirement_events",
    )
    actor = models.CharField(max_length=1000, blank=True)
    actor_old = models.ForeignKey(
        RlcUser, on_delete=models.CASCADE, blank=True, null=True
    )
    text = models.TextField(blank=True)
    accepted = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "event: {}; legalRequirement: {};".format(
            self.id, self.legal_requirement.title
        )

    class Meta:
        verbose_name = "LegalRequirementEvent"
        verbose_name_plural = "LegalRequirementEvents"
