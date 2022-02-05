from apps.api.models import UserProfile
from django.db import models


class LoggedPath(models.Model):
    path = models.CharField(max_length=200)
    user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='logged_paths')
    time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)

    class Meta:
        ordering = ['-time']
        verbose_name = 'LoggedPath'
        verbose_name_plural = 'LoggedPaths'

    def __str__(self):
        return 'loggedPath: {}; path: \'{}\'; user: {};'.format(self.time.strftime('%Y-%m-%d'), self.path,
                                                                self.user.email)
