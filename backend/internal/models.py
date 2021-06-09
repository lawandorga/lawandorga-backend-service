from django.contrib.auth.models import AbstractUser, PermissionsMixin, _user_has_perm, _user_has_module_perms
from solo.models import SingletonModel

from backend.api.models import UserProfile
from tinymce.models import HTMLField

from django.db import models


class InternalUser(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='internal_user')

    class Meta:
        verbose_name = 'InternalUser'
        verbose_name_plural = 'InternalUsers'

    def __str__(self):
        return 'internalUser: {};'.format(self.user.email)


class IndexPage(SingletonModel):
    content = HTMLField()

    class Meta:
        verbose_name = 'IndexPage'
        verbose_name_plural = 'IndexPage'

    def __str__(self):
        return 'IndexPage'


class Article(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    content = HTMLField()
    author = models.ForeignKey(InternalUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-date']

    def __str__(self):
        return 'article: {};'.format(self.title)
