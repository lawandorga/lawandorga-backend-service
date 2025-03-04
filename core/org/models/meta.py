import uuid

from django.db import models


class Meta(models.Model):
    slug = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "ORG_Meta"
        verbose_name_plural = "ORG_Metas"

    def __str__(self):
        return "meta: {}; name: {};".format(self.pk, self.name)
