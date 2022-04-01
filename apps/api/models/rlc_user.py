from apps.api.models.has_permission import HasPermission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from apps.api.models.permission import Permission
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
from django.db import models
from .user import UserProfile


class RlcUser(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='rlc_user')
    # rlc = models.ForeignKey("Rlc", related_name="users", on_delete=models.PROTECT, blank=True, null=True)
    # blocker
    email_confirmed = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # more info
    note = models.TextField(blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=17, null=True, default=None, blank=True)
    street = models.CharField(max_length=255, default=None, null=True, blank=True)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)
    postal_code = models.CharField(max_length=255, default=None, null=True, blank=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'RlcUser'
        verbose_name_plural = 'RlcUsers'
        ordering = ['accepted', 'locked', 'is_active', 'user__name']

    def __str__(self):
        return 'rlcUser: {}; email: {};'.format(self.pk, self.user.email)

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

    def check_delete_is_safe(self):
        from apps.recordmanagement.models import RecordEncryptionNew
        for encryption in self.user.recordencryptions.all():
            if RecordEncryptionNew.objects.filter(record=encryption.record).count() <= 2:
                return False
        return True

    def get_email_confirmation_token(self):
        token = AccountActivationTokenGenerator().make_token(self)
        return token

    def get_email_confirmation_link(self):
        token = self.get_email_confirmation_token()
        link = "{}user/email-confirm/{}/{}/".format(settings.FRONTEND_URL, self.id, token)
        return link

    def send_email_confirmation_email(self):
        link = self.get_email_confirmation_link()
        subject = "Law & Orga Registration"
        message = "Law & Orga - Activate your account here: {}".format(link)
        html_message = loader.render_to_string(
            "email_templates/activate_account.html", {"url": link}
        )
        send_mail(
            subject=subject,
            html_message=html_message,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
        )

    def get_password_reset_token(self):
        token = PasswordResetTokenGenerator().make_token(self.user)
        return token

    def get_password_reset_link(self):
        token = self.get_password_reset_token()
        link = "{}user/password-reset-confirm/{}/{}/".format(settings.FRONTEND_URL, self.id, token)
        return link

    def send_password_reset_email(self):
        link = self.get_password_reset_link()
        subject = "Law & Orga Account Password reset"
        message = "Law & Orga - Reset your password here: {}".format(link)
        html_message = loader.render_to_string(
            "email_templates/reset_password.html", {"link": link}
        )
        send_mail(
            subject=subject,
            html_message=html_message,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
        )

    def grant(self, permission_name):
        permission = Permission.objects.get(name=permission_name)
        HasPermission.objects.create(user_has_permission=self.user, permission=permission)


# this is used on signup
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, rlc_user, timestamp):
        login_timestamp = (
            ""
            if rlc_user.user.last_login is None
            else rlc_user.user.last_login.replace(microsecond=0, tzinfo=None)
        )
        super_make_hash_value = (
            str(rlc_user.pk) + rlc_user.user.password + str(login_timestamp) + str(timestamp)
        )
        additional_hash_value = str(rlc_user.email_confirmed)
        return super_make_hash_value + additional_hash_value
