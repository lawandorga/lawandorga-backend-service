from typing import Optional

from django.db import models
from tinymce.models import HTMLField

from core.auth.models.org_user import Org
from core.models import InternalUser


class Article(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    preview = models.TextField()
    date = models.DateField()
    content = HTMLField()
    recipients = models.ManyToManyField(
        Org,
        related_name="recipients",
        blank=True,
        help_text="The organizations that should receive this article. If empty, all organizations will receive it.",
    )
    author = models.ForeignKey(
        InternalUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "INT_Article"
        verbose_name_plural = "INT_Articles"
        ordering = ["-date"]

    def __str__(self):
        return "article: {};".format(self.title)

    @property
    def author_name(self) -> Optional[str]:
        if self.author is None:
            return None
        return self.author.user.name
