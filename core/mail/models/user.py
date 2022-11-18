import uuid

from django.db import models

from core.auth.models import UserProfile
from core.mail.models.org import MailOrg


class MailUser(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        UserProfile, related_name="mail_user", on_delete=models.CASCADE
    )
    pw_hash = models.CharField(max_length=1000)
    org = models.ForeignKey(MailOrg, related_name="members", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "MailUser"
        verbose_name_plural = "MailUsers"

    def __str__(self):
        return "mailUser: {}; user: {};".format(self.pk, self.user)

    @property
    def email(self):
        address = self.account.addresses.filter(is_default=True).first()
        if address is None:
            return None
        return address.address

    @property
    def aliases(self):
        addresses_1 = list(self.account.addresses.filter(is_default=False).select_related('domain'))
        addresses_2 = map(lambda a: a.address, addresses_1)
        addresses_3 = list(addresses_2)
        return addresses_3

    def check_login_allowed(self):
        return True
