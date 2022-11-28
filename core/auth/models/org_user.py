import uuid
from typing import Any, Dict, List, Union

import ics
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from django.template import loader

from core.auth.domain.user_key import UserKey
from core.auth.token_generator import EmailConfirmationTokenGenerator
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.keys import AsymmetricKey, EncryptedAsymmetricKey
from core.rlc.models import HasPermission, Org, Permission
from core.seedwork.domain_layer import DomainError
from core.seedwork.encryption import EncryptedModelMixin
from core.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
    PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
    PERMISSION_ADMIN_MANAGE_USERS,
)

from .user import UserProfile


class RlcUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user")


class RlcUser(EncryptedModelMixin, models.Model, IOwner):
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
    org = models.ForeignKey(Org, related_name="users", on_delete=models.PROTECT)
    slug = models.UUIDField(default=uuid.uuid4, unique=True)
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
    calendar_uuid = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=True, unique=True
    )
    # settings
    frontend_settings = models.JSONField(null=True, blank=True)
    # encryption
    key = models.JSONField(null=True, blank=True)
    private_key = models.BinaryField(null=True)
    is_private_key_encrypted = models.BooleanField(default=False)
    public_key = models.BinaryField(null=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # custom manager
    objects = RlcUserManager()

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
    def speciality_of_study_display(self):
        return self.get_speciality_of_study_display()

    @property
    def email(self):
        return self.user.email

    @property
    def do_keys_exist(self):
        return self.public_key is not None or self.private_key is not None

    @property
    def locked_legal(self):
        for lr in list(
            self.legal_requirements_user.filter(legal_requirement__accept_required=True)
        ):
            if not lr.accepted:
                return True
        return False

    def check_login_allowed(self):
        if not self.email_confirmed:
            message = "You can not login, yet. Please confirm your email first."
            raise DomainError(message)

        if not self.is_active:
            message = (
                "You can not login. Your account was deactivated by one of your admins."
            )
            raise DomainError(message)

        if not self.accepted:
            message = "You can not login, yet. You need to be accepted as member by one of your admins."
            raise DomainError(message)

    def get_public_key(self) -> bytes:
        return self.get_encryption_key().get_public_key().encode("utf-8")

    def get_private_key(self, *args, **kwargs) -> str:
        return self.get_decryption_key().get_private_key().decode("utf-8")

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union[AsymmetricKey, EncryptedAsymmetricKey]:
        assert self.key is not None
        u = UserKey.create_from_dict(self.key)
        return u.key

    @staticmethod
    def get_dummy_user_private_key(dummy: "RlcUser") -> str:
        if settings.TESTING and dummy.email == "dummy@law-orga.de":
            u1 = UserKey.create_from_dict(dummy.key)
            u2 = u1.decrypt_self(settings.DUMMY_USER_PASSWORD)
            key = u2.key
            assert isinstance(key, AsymmetricKey)
            return key.get_private_key().decode("utf-8")

        raise ValueError("This method is only available for dummy and in test mode.")

    def get_decryption_key(self, *args, **kwargs) -> AsymmetricKey:
        assert self.key is not None

        private_key = cache.get(self.pk, None)

        if settings.TESTING and self.email == "dummy@law-orga.de":
            private_key = RlcUser.get_dummy_user_private_key(self)

        if private_key is None:
            raise ValueError(
                "No private key could be found for user '{}'.".format(self.pk)
            )

        if "key" in self.key:
            public_key = self.key["key"]["public_key"]
        else:
            public_key = self.key["public_key"]

        origin = "A1"

        return AsymmetricKey.create(
            public_key=public_key, private_key=private_key, origin=origin
        )

    def activate_or_deactivate(self):
        self.is_active = not self.is_active

    def update_information(
        self,
        note=None,
        birthday=None,
        phone_number=None,
        street=None,
        city=None,
        postal_code=None,
        speciality_of_study=None,
    ):
        if note is not None:
            self.note = note
        if birthday is not None:
            self.birthday = birthday
        if phone_number is not None:
            self.phone_number = phone_number
        if street is not None:
            self.street = street
        if city is not None:
            self.city = city
        if postal_code is not None:
            self.postal_code = postal_code
        if speciality_of_study is not None:
            self.speciality_of_study = speciality_of_study

    def delete_keys(self):
        self.private_key = None
        self.public_key = None
        self.key = None
        self.is_private_key_encrypted = False
        self.save()

    def __get_as_user_permissions(self) -> List[str]:
        from core.models import HasPermission

        permissions = list(HasPermission.objects.filter(user__id=self.pk))

        return [has_permission.permission.name for has_permission in permissions]

    def __get_as_group_member_permissions(self) -> List[str]:
        from core.models import HasPermission

        groups = [groups["id"] for groups in list(self.groups.values("id"))]

        return [
            has_permission.permission.name
            for has_permission in HasPermission.objects.filter(
                group_has_permission_id__in=groups
            )
        ]

    def get_permissions(self) -> List[str]:
        return (
            self.__get_as_user_permissions() + self.__get_as_group_member_permissions()
        )

    def set_frontend_settings(self, data: Dict[str, Any]):
        self.frontend_settings = data
        self.save(update_fields=["frontend_settings"])

    def generate_keys(self, password: str):
        key = AsymmetricKey.generate()
        u1 = UserKey(key=key)
        u2 = u1.encrypt_self(password)
        self.is_private_key_encrypted = True
        self.key = u2.as_dict()

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

    def check_delete_is_safe(self):
        from core.records.models import RecordEncryptionNew

        for encryption in self.user.rlc_user.recordencryptions.all():
            if (
                RecordEncryptionNew.objects.filter(record=encryption.record).count()
                <= 2
            ):
                return False
        return True

    def get_email_confirmation_token(self):
        token = EmailConfirmationTokenGenerator().make_token(self)
        return token

    def get_email_confirmation_link(self):
        token = self.get_email_confirmation_token()
        link = "{}/user/email-confirm/{}/{}/".format(
            settings.MAIN_FRONTEND_URL, self.id, token
        )
        return link

    def send_email_confirmation_email(self):
        link = self.get_email_confirmation_link()
        subject = "Law&Orga - Registration - Please confirm your email"
        message = "Please confirm your email by opening this link in your browser: {}.".format(
            link
        )
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
        link = "{}/user/password-reset-confirm/{}/{}/".format(
            settings.MAIN_FRONTEND_URL, self.id, token
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

    def grant(self, permission_name=None, permission=None):
        if permission_name:
            p = Permission.objects.get(name=permission_name)
        elif permission:
            p = permission
        else:
            raise ValueError("You need to pass 'permission_name' or 'permission'")
        HasPermission.objects.create(user=self, permission=p)

    def __has_as_user_permission(self, permission):
        from core.models import HasPermission

        return HasPermission.objects.filter(user=self, permission=permission).exists()

    def __has_as_group_member_permission(self, permission):
        groups = [group.pk for group in self.groups.all()]
        from core.models import HasPermission

        return HasPermission.objects.filter(
            group_has_permission__pk__in=groups, permission=permission
        ).exists()

    def has_permission(self, permission: Union[str, "Permission"]):
        if isinstance(permission, str):
            try:
                from core.models import Permission

                permission = Permission.objects.get(name=permission)
            except ObjectDoesNotExist:
                return False

        as_user = self.__has_as_user_permission(permission)
        if as_user:
            return True

        as_group = self.__has_as_group_member_permission(permission)
        if as_group:
            return True

    def get_badges(self):
        from core.records.models import RecordAccess, RecordDeletion

        # profiles
        profiles = RlcUser.objects.filter(org=self.org, locked=True).count()
        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            profiles += RlcUser.objects.filter(org=self.org, accepted=False).count()

        # deletion requests
        if self.has_permission(PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS):
            record_deletion_requests = RecordDeletion.objects.filter(
                record__template__rlc=self.org, state="re"
            ).count()
        else:
            record_deletion_requests = 0

        # permit requests
        if self.has_permission(PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS):
            record_permit_requests = RecordAccess.objects.filter(
                record__template__rlc=self.org, state="re"
            ).count()
        else:
            record_permit_requests = 0

        # legal
        legal = 0
        for lr in list(self.legal_requirements_user.all()):
            if not lr.accepted:
                legal += 1

        # return
        data = {
            "profiles": profiles,
            "record_deletion_requests": record_deletion_requests,
            "record_permit_requests": record_permit_requests,
            "legal": legal,
        }
        return data

    def get_ics_calendar(self):
        from ...events.models import Event

        events = (
            (
                self.org.events.all()
                | Event.objects.filter(is_global=True).filter(org__meta=self.org.meta)
            )
            if (self.org.meta is not None)
            else self.org.events.all()
        )

        c = ics.Calendar()
        for rlcEvent in events:
            e = ics.Event()
            e.name = rlcEvent.name
            e.begin = rlcEvent.start_time
            e.end = rlcEvent.end_time
            e.description = rlcEvent.description
            e.organizer = rlcEvent.org.name
            c.events.add(e)
        return c.serialize()

    def regenerate_calendar_uuid(self):
        self.calendar_uuid = uuid.uuid4()
        self.save()
