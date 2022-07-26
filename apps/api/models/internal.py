from django.db import models
from solo.models import SingletonModel
from tinymce.models import HTMLField

from apps.api.models import UserProfile


class InternalUser(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="internal_user"
    )

    class Meta:
        verbose_name = "InternalUser"
        verbose_name_plural = "InternalUsers"

    def __str__(self):
        return "internalUser: {};".format(self.user.email)


class IndexPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = "IndexPage"
        verbose_name_plural = "IndexPage"

    def __str__(self):
        return "IndexPage"


class ImprintPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = "ImprintPage"
        verbose_name_plural = "ImprintPage"

    def __str__(self):
        return "ImprintPage"


class TomsPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = "TomsPage"
        verbose_name_plural = "TomsPage"

    def __str__(self):
        return "TomsPage"


class HelpPage(SingletonModel):
    manual = models.FileField("Manual", upload_to="internal/helppage/manual/")

    class Meta:
        verbose_name = "HelpPage"
        verbose_name_plural = "HelpPage"

    def __str__(self):
        return "HelpPage"


class Article(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    content = HTMLField()
    author = models.ForeignKey(
        InternalUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-date"]

    def __str__(self):
        return "article: {};".format(self.title)


class RoadmapItem(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()

    class Meta:
        verbose_name = "RoadmapItem"
        verbose_name_plural = "RoadmapItems"
        ordering = ["date"]

    def __str__(self):
        return "roadmapItem: {};".format(self.title)
