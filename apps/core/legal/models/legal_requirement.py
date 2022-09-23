from django.db import models
from tinymce import models as tinymce_models

from apps.core.auth.models import RlcUser


class LegalRequirement(models.Model):
    title = models.CharField(max_length=1000)
    content = tinymce_models.HTMLField()
    accept_required = models.BooleanField()
    rlc_users = models.ManyToManyField(
        RlcUser, through="LegalRequirementUser", related_name="legal_requirements"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "legalRequirement: {}; title: {};".format(self.id, self.title)

    class Meta:
        verbose_name = "LegalRequirement"
        verbose_name_plural = "LegalRequirements"


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
        LegalRequirementUser, on_delete=models.CASCADE, related_name="events"
    )
    actor = models.ForeignKey(RlcUser, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField(blank=True)
    accepted = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "event: {}; legalRequirement: {};".format(
            self.id, self.legal_requirement_user.legal_requirement.title
        )

    class Meta:
        verbose_name = "LegalRequirementEvent"
        verbose_name_plural = "LegalRequirementEvents"
