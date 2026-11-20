from typing import Optional

from django.db import models

from .landing import public_file_url


class RoadmapItem(models.Model):
    STATUS_LIVE = "live"
    STATUS_PLANNED = "planned"
    STATUS_CHOICES = [
        (STATUS_LIVE, "Live"),
        (STATUS_PLANNED, "Planned"),
    ]

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED
    )
    stage = models.CharField(
        max_length=40, blank=True, help_text='For example "Prototyp".'
    )
    benefits = models.TextField(blank=True, help_text="One benefit per line.")
    status_note = models.CharField(
        max_length=200, blank=True, help_text='Shown as "Stand: …".'
    )
    icon = models.ImageField(upload_to="internal/landing/roadmap/icons/", blank=True)
    position = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "INT_RoadmapItem"
        verbose_name_plural = "INT_RoadmapItems"
        ordering = ["status", "position", "-date"]

    def __str__(self):
        return "roadmapItem: {};".format(self.title)

    @property
    def benefit_list(self) -> list[str]:
        return [line.strip() for line in self.benefits.splitlines() if line.strip()]

    @property
    def icon_url(self) -> Optional[str]:
        return public_file_url(self.icon)
