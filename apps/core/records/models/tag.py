from django.db import models

from apps.core.models import Org


class Tag(models.Model):
    rlc = models.ForeignKey(
        Org, on_delete=models.CASCADE, blank=True, related_name="tags"
    )
    name = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["rlc", "name"]

    def __str__(self):
        return "tag: {}; name: {}; rlc: {};".format(self.pk, self.name, self.rlc)
