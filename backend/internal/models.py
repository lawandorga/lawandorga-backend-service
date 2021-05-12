from django.contrib.auth.models import AbstractUser, PermissionsMixin, _user_has_perm, _user_has_module_perms
from backend.api.models import UserProfile
from tinymce.models import HTMLField

from django.db import models


class InternalUser(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='internal_role')
    is_active = True  # used for django internal permission stuff
    is_anonymous = False  # used for django internal permission stuff

    class Meta:
        verbose_name = 'InternalUser'
        verbose_name_plural = 'InternalUsers'

    def __str__(self):
        return 'internUser: {};'.format(self.user.email)


class Article(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField()
    content = HTMLField()
    author = models.ForeignKey(InternalUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return 'article: {};'.format(self.title)
