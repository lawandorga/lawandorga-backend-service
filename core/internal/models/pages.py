from typing import Optional

from django.db import models
from solo.models import SingletonModel
from tinymce.models import HTMLField


class IndexPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = "INT_IndexPage"
        verbose_name_plural = "INT_IndexPage"

    def __str__(self):
        return "IndexPage"


class ImprintPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = "INT_ImprintPage"
        verbose_name_plural = "INT_ImprintPage"

    def __str__(self):
        return "ImprintPage"


class TomsPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = "INT_TomsPage"
        verbose_name_plural = "INT_TomsPage"

    def __str__(self):
        return "TomsPage"


class HelpPage(SingletonModel):
    manual = models.FileField("Manual", upload_to="internal/helppage/manual/")

    class Meta:
        verbose_name = "INT_HelpPage"
        verbose_name_plural = "INT_HelpPage"

    def __str__(self):
        return "HelpPage"

    @property
    def manual_url(self) -> Optional[str]:
        if self.manual:
            return self.manual.url
        return None
