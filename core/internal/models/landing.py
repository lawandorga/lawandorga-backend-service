from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import FieldFile


def public_file_url(file: Optional[FieldFile]) -> Optional[str]:
    """Return a URL for an uploaded landing page image that works on a public
    page.

    In production the default storage is S3 and returns absolute (signed)
    URLs, which are returned unchanged. The local file system storage returns
    relative URLs; those are prefixed with MAIN_BACKEND_URL, if it is set.
    """
    if not file:
        return None
    url = file.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    backend = getattr(settings, "MAIN_BACKEND_URL", "")
    if not backend:
        return "/{}".format(url.lstrip("/"))
    return "{}/{}".format(backend.rstrip("/"), url.lstrip("/"))


class FeatureArea(models.Model):
    """One area of Law&Orga shown on the public landing page, either in the
    scroll-driven showroom or in the "Außerdem in Law&Orga" list."""

    PLACEMENT_SHOWROOM = "showroom"
    PLACEMENT_MORE = "more"
    PLACEMENT_CHOICES = [
        (PLACEMENT_SHOWROOM, "Showroom"),
        (PLACEMENT_MORE, "Außerdem in Law&Orga"),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(
        upload_to="internal/landing/feature_areas/icons/", blank=True
    )
    screenshot = models.ImageField(
        upload_to="internal/landing/feature_areas/screenshots/",
        blank=True,
        help_text="Only screenshots with demo data. They are shown on a public page.",
    )
    screenshot_alt = models.CharField(
        max_length=300,
        blank=True,
        help_text="Alternative text for the screenshot. Required when a screenshot is set.",
    )
    screenshot_note = models.CharField(
        max_length=200,
        blank=True,
        help_text="Caption below the screenshot. If empty, a default caption is shown.",
    )
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    position = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "INT_FeatureArea"
        verbose_name_plural = "INT_FeatureAreas"
        ordering = ["placement", "position"]

    def __str__(self):
        return "featureArea: {}; placement: {};".format(self.title, self.placement)

    def clean(self):
        super().clean()
        if self.screenshot and not self.screenshot_alt.strip():
            raise ValidationError(
                {"screenshot_alt": "An alternative text is required for a screenshot."}
            )

    @property
    def icon_url(self) -> Optional[str]:
        return public_file_url(self.icon)

    @property
    def screenshot_url(self) -> Optional[str]:
        return public_file_url(self.screenshot)
