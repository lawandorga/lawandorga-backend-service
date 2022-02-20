from apps.api.models import Rlc
from django.db import models


class Note(models.Model):
    rlc = models.ForeignKey(Rlc, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created']

    def __str__(self):
        return 'rlc: {}; note: {};'.format(self.rlc.name, self.title)
