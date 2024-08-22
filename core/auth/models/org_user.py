from datetime import timedelta
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Type,
    TypedDict,
    Union,
)
from uuid import UUID, uuid4

import ics
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.template import loader
from django.utils import timezone

from core.auth.domain.user_key import UserKey
from core.auth.token_generator import EmailConfirmationTokenGenerator
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.permissions.models import HasPermission, Permission
from core.permissions.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
    PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from core.rlc.models import Org, OrgEncryption
from core.seedwork.aggregate import Aggregate
from core.seedwork.domain_layer import DomainError
from core.seedwork.events_addon import EventsAddon
from messagebus import Event

from .user import UserProfile
from seedwork.functional import list_filter, list_map

if TYPE_CHECKING:
    from core.auth.models.mfa import MultiFactorAuthenticationSecret
    from core.folders.domain.value_objects.folder_key import EncryptedFolderKeyOfUser
    from core.rlc.models.group import Group


class KeyOfUser(TypedDict):
    id: int
    correct: bool
    source: str
    information: str
    group_id: int | None


class EmailTokenValidator(Protocol):
    def check_token(self, user: "OrgUser", token: str) -> bool: ...


class RlcUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user")


class OrgUser(Aggregate, models.Model):
    class OrgUserLocked(Event):
        org_user_uuid: UUID
        org_pk: int

    class OrgUserUnlocked(Event):
        org_user_uuid: UUID
        by_org_user_uuid: UUID
        org_pk: int

    @staticmethod
    def create(
        org: Org,
        email: str,
        name: str,
        password: str,
        email_confirmed=False,
        accepted=False,
        pk=0,
        user_pk=0,
    ) -> "OrgUser":
        user = UserProfile(email=email, name=name)
        if user_pk:
            user.pk = user_pk
        user.set_password(password)
        rlc_user = OrgUser(
            user=user, email_confirmed=email_confirmed, accepted=accepted, org=org
        )
        if pk:
            rlc_user.pk = pk
        rlc_user.generate_keys(password)
        return rlc_user

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
    uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)
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
        primary_key=False, default=uuid4, editable=True, unique=True
    )
    # settings
    frontend_settings = models.JSONField(null=True, blank=True)
    # encryption
    key = models.JSONField(null=False, blank=True)
    old_private_key = models.BinaryField(null=True)
    is_private_key_encrypted = models.BooleanField(default=False)
    old_public_key = models.BinaryField(null=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # custom manager
    objects = RlcUserManager()
    # addons
    addons = {"events": EventsAddon}
    events: EventsAddon

    if TYPE_CHECKING:
        mfa_secret: "MultiFactorAuthenticationSecret"
        groups: models.QuerySet[Group]
        org_id: int
        user_id: int

    class Meta:
        verbose_name = "AUT_OrgUser"
        verbose_name_plural = "AUT_OrgUsers"
        ordering = ["accepted", "locked", "is_active", "user__name"]

    def __str__(self):
        return "orgUser: {}; email: {};".format(self.pk, self.user.email)

    @property
    def org_key(self) -> KeyOfUser:
        _keys1 = self.user.users_rlc_keys.select_related("rlc").all()
        _keys2 = list(_keys1)
        assert len(_keys2) == 1
        key = _keys2[0]
        return {
            "id": key.pk,
            "information": self.org.name,
            "source": "ORG",
            "correct": key.correct,
            "group_id": None,
        }

    @property
    def last_login_month(self):
        return self.user.last_login_month

    @property
    def user_key(self) -> KeyOfUser:
        self.get_private_key()
        return {
            "id": 0,
            "information": self.name,
            "source": "USER",
            "correct": True,
            "group_id": None,
        }

    @property
    def group_keys(self) -> list[KeyOfUser]:
        groups = self.get_groups()
        _keys0 = list_map(groups, lambda x: (x, x.get_enc_group_key_of_user(self)))
        _keys2 = list_filter(_keys0, lambda k: k[1] is not None)
        _keys3: list[KeyOfUser] = []
        for key in _keys2:
            _keys3.append(
                {
                    "id": 0,
                    "correct": getattr(key[1], "is_valid"),
                    "source": "GROUP",
                    "information": key[0].name,
                    "group_id": key[0].pk,
                }
            )
        return _keys3

    @property
    def raw_folder_keys(self) -> list["EncryptedFolderKeyOfUser"]:
        from core.folders.infrastructure.folder_repository import DjangoFolderRepository

        r = DjangoFolderRepository()
        folders = r.get_list(self.org_id)

        folder_keys: list["EncryptedFolderKeyOfUser"] = []
        for folder in folders:
            for key in folder.keys:
                if key.TYPE == "FOLDER" and key.owner_uuid == self.uuid:
                    folder_keys.append(key)

        return folder_keys

    @property
    def folder_keys(self) -> list[KeyOfUser]:
        from core.folders.infrastructure.folder_repository import DjangoFolderRepository

        r = DjangoFolderRepository()
        folders = r.get_list(self.org_id)

        folder_keys: list[KeyOfUser] = []
        for folder in folders:
            for key in folder.keys:
                if key.TYPE == "FOLDER" and key.owner_uuid == self.uuid:
                    folder_keys.append(
                        {
                            "id": 0,
                            "correct": key.is_valid,
                            "source": "FOLDER",
                            "information": folder.name,
                            "group_id": None,
                        }
                    )

        return folder_keys

    @property
    def all_keys_correct(self):
        _keys = self.keys
        for key in _keys:
            if not key["correct"]:
                return False
        return True

    @property
    def keys(self) -> list[KeyOfUser]:
        return [self.org_key, self.user_key] + self.folder_keys + self.group_keys

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
        from core.legal.models import LegalRequirement

        return LegalRequirement.is_locked(self)

    @property
    def members_information(self):
        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            members_data = []
            users = OrgUser.objects.filter(
                org=self.org, created__gt=(timezone.now() - timedelta(days=14))
            )
            for rlc_user in list(users):
                if rlc_user.groups.all().count() == 0:
                    members_data.append(
                        {
                            "name": rlc_user.user.name,
                            "id": rlc_user.user.pk,
                            "rlcuserid": rlc_user.pk,
                        }
                    )
            return members_data
        return None

    @property
    def own_records(self):
        from core.data_sheets.models import DataSheet

        records = DataSheet.objects.filter(template__rlc=self.org).prefetch_related(
            "users_entries", "users_entries__value"
        )
        record_pks = []
        for record in list(records):
            users_entries = list(record.users_entries.all())
            if len(users_entries) <= 0:
                continue
            users = list(users_entries[0].value.all())
            if self.pk in map(lambda x: x.id, users):
                record_pks.append(record.pk)

        return DataSheet.objects.filter(pk__in=record_pks)

    @property
    def information(self) -> Dict[str, Any]:
        return_dict = {}
        # members
        members_data = self.members_information
        if members_data:
            return_dict["members"] = members_data
        return return_dict

    def get_group_uuids(self) -> list[UUID]:
        if not hasattr(self, "_group_uuids"):
            self._group_uuids = list(self.groups.values_list("uuid", flat=True))
        return self._group_uuids

    def get_groups(self) -> list["Group"]:
        return list(self.groups.all())

    def test_keys(self) -> list[models.Model]:
        org_key: Optional[OrgEncryption] = self.user.users_rlc_keys.first()
        assert org_key is not None
        correct = org_key.test(self.get_private_key())
        if not correct:
            self.locked = True
            return [org_key, self]
        return []

    def get_decrypted_key_from_password(self, password: str) -> UserKey:
        enc_user_key = UserKey.create_from_dict(self.key)
        user_key = enc_user_key.decrypt_self(password)
        return user_key

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
    def get_dummy_user_private_key(dummy: "OrgUser", email="dummy@law-orga.de") -> str:
        if settings.TESTING and dummy.email == email:
            u1 = UserKey.create_from_dict(dummy.key)
            u2 = u1.decrypt_self(settings.DUMMY_USER_PASSWORD)
            key = u2.key
            assert isinstance(key, AsymmetricKey)
            return key.get_private_key().decode("utf-8")

        raise ValueError("This method is only available for dummy and in test mode.")

    def __get_session(self) -> Optional[Session]:
        memory_cache_session_key = "session-of-org-user-{}".format(self.pk)
        memory_cache_time_key = "time-of-org-user-{}".format(self.pk)

        if hasattr(self.__class__, memory_cache_session_key) and hasattr(
            self.__class__, memory_cache_time_key
        ):
            if timezone.now() < getattr(self.__class__, memory_cache_time_key):
                return getattr(self.__class__, memory_cache_session_key)
            else:
                delattr(self.__class__, memory_cache_time_key)
                delattr(self.__class__, memory_cache_session_key)

        session = None
        for s in list(Session.objects.all()):
            decoded: dict[str, str] = s.get_decoded()
            if "_auth_user_id" in decoded and decoded["_auth_user_id"] == str(
                self.user_id
            ):
                session = s
                break

        if session is None:
            return None

        setattr(
            self.__class__,
            memory_cache_time_key,
            timezone.now() + timedelta(seconds=10),
        )
        setattr(self.__class__, memory_cache_session_key, session)

        return session

    def get_decryption_key(self, *args, **kwargs) -> AsymmetricKey:
        assert self.key is not None

        if settings.TESTING and (
            self.email == "dummy@law-orga.de" or self.email == "tester@law-orga.de"
        ):
            public_key = self.key["key"]["public_key"]
            private_key = OrgUser.get_dummy_user_private_key(self, self.email)
            origin = self.key["key"]["origin"]
            return AsymmetricKey.create(
                private_key=private_key, origin=origin, public_key=public_key
            )

        session = self.__get_session()

        if session is None:
            raise ValueError(
                "No private key could be found for user '{}'.".format(self.pk)
            )

        decoded = session.get_decoded()
        key = UserKey.create_from_unsafe_dict(decoded["user_key"])

        assert isinstance(key.key, AsymmetricKey), f"key is no of type: {type(key.key)}"
        return key.key

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

    def __get_as_user_permissions(self) -> List[str]:
        permissions = list(HasPermission.objects.filter(user__id=self.pk))

        return [has_permission.permission.name for has_permission in permissions]

    def __get_as_group_member_permissions(self) -> List[str]:
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

    def set_frontend_settings(self, data: dict[str, Any]):
        self.frontend_settings = data
        self.save(update_fields=["frontend_settings"])

    def generate_keys(self, password: str):
        key = AsymmetricKey.generate(AsymmetricEncryptionV1)
        u1 = UserKey(key=key)
        u2 = u1.encrypt_self(password)
        self.is_private_key_encrypted = True
        self.key = u2.as_dict()

    def lock(self) -> None:
        self.locked = True
        self.events.add(
            OrgUser.OrgUserLocked(org_user_uuid=self.uuid, org_pk=self.org_id)
        )

    def change_password_for_keys(self, new_password: str):
        key = self.get_decryption_key()
        u1 = UserKey(key=key)
        u2 = u1.encrypt_self(new_password)
        self.is_private_key_encrypted = True
        self.key = u2.as_dict()

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

    def check_delete_is_safe(self) -> tuple[bool, str]:
        from core.folders.infrastructure.folder_repository import DjangoFolderRepository

        r = DjangoFolderRepository()
        folders = r.get_list(self.org_id)

        dangerous_folders: list[str] = []
        safe = True

        for folder in folders:
            total_keys = (
                len(folder.keys) + len(folder.group_keys) + 1 if folder.parent else 0
            )
            if folder.has_access(self) and total_keys <= 3:
                dangerous_folders.append(folder.name)
                safe = False

        return safe, ", ".join(dangerous_folders)

    def get_email_confirmation_token(self):
        token = EmailConfirmationTokenGenerator().make_token(self)
        return token

    def get_email_confirmation_link(self):
        token = self.get_email_confirmation_token()
        link = "{}/user/email-confirm/{}/{}/".format(
            settings.MAIN_FRONTEND_URL, self.pk, token
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

    def confirm_email(self, token_validator: Type[EmailTokenValidator], token: str):
        if token_validator().check_token(self, token):
            self.email_confirmed = True
        else:
            raise DomainError(
                "The confirmation link is invalid, possibly because it has already been used."
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
        return HasPermission.objects.filter(user=self, permission=permission).exists()

    def __has_as_group_member_permission(self, permission):
        groups = [group.pk for group in self.groups.all()]

        return HasPermission.objects.filter(
            group_has_permission__pk__in=groups, permission=permission
        ).exists()

    def has_permission_as_user(self, permission: Union[str, "Permission"]) -> bool:
        if isinstance(permission, str):
            try:
                from core.models import Permission

                permission = Permission.objects.get(name=permission)
            except ObjectDoesNotExist:
                return False

        return self.__has_as_user_permission(permission)

    def has_permission(self, permission: Union[str, "Permission"]) -> bool:
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

        return False

    @property
    def badges(self):
        from core.legal.models.legal_requirement import LegalRequirement
        from core.records.models.access import RecordsAccessRequest
        from core.records.models.deletion import RecordsDeletion

        # profiles
        profiles = OrgUser.objects.filter(org=self.org, locked=True).count()
        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            profiles += OrgUser.objects.filter(org=self.org, accepted=False).count()

        # deletion requests
        if self.has_permission(PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS):
            record_deletion_requests = RecordsDeletion.objects.filter(
                requestor__org=self.org, state="re"
            ).count()
        else:
            record_deletion_requests = 0

        # permit requests
        if self.has_permission(PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS):
            record_permit_requests = RecordsAccessRequest.objects.filter(
                requestor__org=self.org, state="re"
            ).count()
        else:
            record_permit_requests = 0

        # legal
        legal = 0
        for lr in list(LegalRequirement.objects.all()):
            if not lr.is_accepted(self):
                legal += 1

        # record
        record = 0
        record += RecordsAccessRequest.objects.filter(
            requestor__org_id=self.org_id, state="re"
        ).count()
        record += RecordsDeletion.objects.filter(
            requestor__org_id=self.org_id, state="re"
        ).count()

        # return
        data = {
            "profiles": profiles,
            "record_deletion_requests": record_deletion_requests,
            "record_permit_requests": record_permit_requests,
            "legal": legal,
            "record": record,
        }
        return data

    def get_ics_calendar(self):
        from ...events.models import EventsEvent

        events = EventsEvent.objects.filter(
            Q(level="META", org__meta=self.org.meta)
            | Q(level="GLOBAL")
            | Q(org=self.org)
        )

        c = ics.Calendar()
        for rlc_event in events:
            e = ics.Event()
            e.name = rlc_event.name
            e.begin = rlc_event.start_time
            e.end = rlc_event.end_time
            e.description = rlc_event.description
            e.organizer = rlc_event.org.name
            c.events.add(e)
        return c.serialize()

    def regenerate_calendar_uuid(self):
        self.calendar_uuid = uuid4()
        self.save()

    def fix_keys(self, by: "OrgUser"):
        assert self.org_id == by.org_id

        aes_key_rlc = by.org.get_aes_key(
            user=by.user, private_key_user=by.get_private_key()
        )
        new_keys = OrgEncryption(
            user=self.user, rlc=self.org, encrypted_key=aes_key_rlc
        )

        self.user.users_rlc_keys.all().delete()

        new_keys.encrypt(self.get_public_key())
        new_keys.save()

    def unlock(self, by: "OrgUser"):
        self.fix_keys(by)
        self.locked = False
        self.events.add(
            OrgUser.OrgUserUnlocked(
                org_user_uuid=self.uuid,
                by_org_user_uuid=by.uuid,
                org_pk=self.org_id,
            )
        )
