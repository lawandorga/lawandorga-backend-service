from binascii import hexlify
from random import randbytes

from django.db import models

from .org_user import RlcUser
from .user import UserProfile


class MatrixUser(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="matrix_user"
    )
    id = models.CharField(max_length=8, primary_key=True, editable=False)
    _group = models.CharField(max_length=255, null=True, blank=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MatrixUser"
        verbose_name_plural = "MatrixUsers"
        ordering = ["user__name"]

    def __str__(self):
        return "matrixUser: {}; localpart: {}; group: {};".format(
            self.user.name, self.pk, self.group
        )

    def save(self, **kwargs):
        if not self.id:
            id = hexlify(randbytes(4)).decode()
            while MatrixUser.objects.filter(id=id).exists():
                id = hexlify(randbytes(4)).decode()
            self.id = id
        super().save(**kwargs)

    @property
    def group(self):
        if self._group:
            return self._group
        try:
            rlc_user = RlcUser.objects.get(user=self.user)
            return rlc_user.org.name
        except RlcUser.DoesNotExist:
            return ""
