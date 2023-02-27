from binascii import hexlify
from random import randbytes

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .org_user import RlcUser
from .user import UserProfile


class MatrixUser(models.Model):
    @staticmethod
    def create(user: UserProfile, group: str | None = None) -> "MatrixUser":
        matrix_user = MatrixUser(user=user)
        if group is not None:
            matrix_user._group = group
        return matrix_user

    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="matrix_user"
    )
    matrix_id = models.CharField(max_length=8, editable=False, unique=True)
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
        if not self.matrix_id:
            matrix_id = hexlify(randbytes(4)).decode()
            while MatrixUser.objects.filter(matrix_id=matrix_id).exists():
                matrix_id = hexlify(randbytes(4)).decode()
            self.matrix_id = matrix_id
        super().save(**kwargs)

    @property
    def group(self):
        if self._group:
            return self._group
        try:
            rlc_user = RlcUser.objects.get(user=self.user)
            return rlc_user.org.name
        except ObjectDoesNotExist:
            return ""
