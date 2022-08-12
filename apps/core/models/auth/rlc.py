from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import models
from django.template import loader
from apps.static.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption
from .user import UserProfile
from apps.core.models.rlc import Permission, HasPermission


class RlcUser(EncryptedModelMixin, models.Model):
    STUDY_CHOICES = (
        ("LAW", "Law Sciences"),
        ("PSYCH", "Psychology"),
        ("POL", "Political Science"),
        ("SOC", "Social Sciences"),
        ("ECO", "Economics"),
        ("MED", "Medicine / Medical Psychology"),
        ("PHA", "Pharmacy"),
        ("CUL", "Cultural Studies"),
        ("OTHER", "Other"),
        ("NONE", "None"),
    )
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="rlc_user"
    )
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
    speciality_of_study = models.CharField(
        choices=STUDY_CHOICES, max_length=100, blank=True, null=True
    )
    # encryption
    private_key = models.BinaryField(null=True)
    is_private_key_encrypted = models.BooleanField(default=False)
    public_key = models.BinaryField(null=True)
    encryption_class = AESEncryption
    encrypted_fields = ["private_key"]
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RlcUser"
        verbose_name_plural = "RlcUsers"
        ordering = ["accepted", "locked", "is_active", "user__name"]

    def __str__(self):
        return "rlcUser: {}; email: {};".format(self.pk, self.user.email)

    @property
    def name(self):
        return self.user.name

    @property
    def email(self):
        return self.user.email

    @property
    def do_keys_exist(self):
        return self.public_key is not None or self.private_key is not None

    def encrypt(self, password=None):
        if password is not None:
            key = password
        else:
            raise ValueError("You need to pass (password).")

        super().encrypt(key)

        if not self.is_private_key_encrypted:
            self.is_private_key_encrypted = True
            self.save()

    def decrypt(self, password=None):
        if password is not None:
            key = password
        else:
            raise ValueError("You need to pass (password).")

        if not self.is_private_key_encrypted:
            self.encrypt(key)
            self.is_private_key_encrypted = True
            self.save()

        super().decrypt(key)

    def delete_keys(self):
        self.private_key = None
        self.public_key = None
        self.is_private_key_encrypted = False
        self.save()

    def generate_keys(self):
        self.private_key, self.public_key = RSAEncryption.generate_keys()
        self.is_private_key_encrypted = False
        self.save()

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

    def check_delete_is_safe(self):
        from apps.recordmanagement.models import RecordEncryptionNew

        for encryption in self.user.recordencryptions.all():
            if (
                RecordEncryptionNew.objects.filter(record=encryption.record).count()
                <= 2
            ):
                return False
        return True

    def get_email_confirmation_token(self):
        token = AccountActivationTokenGenerator().make_token(self)
        return token

    def get_email_confirmation_link(self):
        token = self.get_email_confirmation_token()
        link = "{}user/email-confirm/{}/{}/".format(
            settings.FRONTEND_URL, self.id, token
        )
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
        link = "{}user/password-reset-confirm/{}/{}/".format(
            settings.FRONTEND_URL, self.id, token
        )
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
        HasPermission.objects.create(
            user_has_permission=self.user, permission=permission
        )


# this is used on signup
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, rlc_user, timestamp):
        super_make_hash_value = (
            str(rlc_user.pk)
            + rlc_user.user.password
            + str(timestamp)
        )
        additional_hash_value = str(rlc_user.email_confirmed)
        return super_make_hash_value + additional_hash_value
