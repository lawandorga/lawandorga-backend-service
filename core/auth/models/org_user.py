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
    cast,
)
from uuid import UUID, uuid4

import ics
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from django.template import loader
from django.utils import timezone

from core.auth.domain.user_key import UserKey
from core.auth.token_generator import EmailConfirmationTokenGenerator
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.rlc.models import HasPermission, Org, OrgEncryption, Permission
from core.seedwork.aggregate import Aggregate
from core.seedwork.domain_layer import DomainError
from core.seedwork.events_addon import EventsAddon
from core.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
    PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from messagebus import EventData

from ...folders.domain.repositiories.folder import FolderRepository
from ...seedwork.repository import RepositoryWarehouse
from .user import UserProfile

if TYPE_CHECKING:
    from core.auth.models.mfa import MultiFactorAuthenticationSecret


class OrgUserLocked(EventData):
    org_user_uuid: UUID
    org_pk: int


class OrgUserUnlocked(EventData):
    org_user_uuid: UUID
    by_org_user_uuid: UUID
    org_pk: int


class KeyOfUser(TypedDict):
    id: int
    correct: bool
    source: str
    information: str


class EmailTokenValidator(Protocol):
    def check_token(self, rlc_user: "RlcUser", token: str) -> bool:
        ...


class RlcUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user")


class RlcUser(Aggregate, models.Model):
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
    ) -> "RlcUser":
        user = UserProfile(email=email, name=name)
        if user_pk:
            user.pk = user_pk
        user.set_password(password)
        rlc_user = RlcUser(
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
    # typing
    mfa_secret: "MultiFactorAuthenticationSecret"

    class Meta:
        verbose_name = "RlcUser"
        verbose_name_plural = "RlcUsers"
        ordering = ["accepted", "locked", "is_active", "user__name"]

    def __str__(self):
        return "rlcUser: {}; email: {};".format(self.pk, self.user.email)

    @property
    def org_key(self) -> KeyOfUser:
        _keys1 = self.user.users_rlc_keys.select_related("rlc").all()
        _keys2 = list(_keys1)
        assert len(_keys2) == 1
        key = _keys2[0]
        return {
            "id": key.id,
            "information": self.org.name,
            "source": "ORG",
            "correct": key.correct,
        }

    @property
    def user_key(self) -> KeyOfUser:
        self.get_private_key()
        return {"id": 0, "information": self.name, "source": "USER", "correct": True}

    @property
    def record_keys(self) -> list[KeyOfUser]:
        from core.records.models import RecordEncryptionNew

        _keys1 = RecordEncryptionNew.objects.filter(user_id=self.id).select_related(
            "record"
        )
        _keys2 = list(_keys1)
        _keys3: list[KeyOfUser] = []
        for key in _keys2:
            _keys3.append(
                {
                    "id": key.id,
                    "correct": key.correct,
                    "source": "RECORD",
                    "information": "{}".format(key.record.identifier),
                }
            )
        return _keys3

    @property
    def folder_keys(self) -> list[KeyOfUser]:
        from core.folders.infrastructure.folder_repository import FolderRepository

        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
        folders = r.get_list(self.org_id)

        folder_keys = []
        for folder in folders:
            for key in folder.keys:
                if key.TYPE == "FOLDER" and key.owner.uuid == self.uuid:
                    key = {
                        "id": 0,
                        "correct": key.is_valid,
                        "source": "FOLDER",
                        "information": folder.name,
                    }
                    folder_keys.append(key)

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
        return [self.org_key, self.user_key] + self.record_keys + self.folder_keys

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

    @property
    def records_information(self):
        from core.records.models import Record

        records = Record.objects.filter(template__rlc=self.org).prefetch_related(
            "state_entries", "users_entries", "users_entries__value"
        )
        records_data = []
        for record in list(records):
            state_entries = list(record.state_entries.all())
            users_entries = list(record.users_entries.all())

            if len(users_entries) <= 0 or len(state_entries) <= 0:
                continue
            users = list(users_entries[0].value.all())
            if self.id not in map(lambda x: x.id, users):
                continue
            state = state_entries[0].value
            if state == "Open":
                records_data.append(
                    {
                        "id": record.id,
                        "uuid": record.uuid,
                        "identifier": record.identifier,
                        "state": state,
                    }
                )

        return records_data

    @property
    def members_information(self):
        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            members_data = []
            users = RlcUser.objects.filter(
                org=self.org, created__gt=(timezone.now() - timedelta(days=14))
            )
            for rlc_user in list(users):
                if rlc_user.groups.all().count() == 0:
                    members_data.append(
                        {
                            "name": rlc_user.user.name,
                            "id": rlc_user.user.id,
                            "rlcuserid": rlc_user.id,
                        }
                    )
            return members_data
        return None

    @property
    def questionnaire_information(self):
        from core.questionnaires.models.questionnaire import Questionnaire

        questionnaires = Questionnaire.objects.filter(
            template__rlc_id=self.org_id
        ).select_related("template", "record")

        questionnaire_data = []

        for questionnaire in list(questionnaires):
            if (
                not questionnaire.answered
                and questionnaire.folder_uuid
                and questionnaire.folder.has_access(self)
            ):
                questionnaire_data.append(
                    {
                        "name": questionnaire.name,
                        "folder_uuid": questionnaire.folder_uuid,
                    }
                )

        return questionnaire_data

    @property
    def own_records(self):
        from core.records.models import Record

        records = Record.objects.filter(template__rlc=self.org).prefetch_related(
            "users_entries", "users_entries__value"
        )
        record_pks = []
        for record in list(records):
            users_entries = list(record.users_entries.all())
            if len(users_entries) <= 0:
                continue
            users = list(users_entries[0].value.all())
            if self.id in map(lambda x: x.id, users):
                record_pks.append(record.id)

        return Record.objects.filter(pk__in=record_pks)

    @property
    def changed_records_information(self):
        records = self.own_records
        records = records.filter(updated__gt=timezone.now() - timedelta(days=10))
        changed_records_data = []
        for record in list(records):
            changed_records_data.append(
                {
                    "id": record.id,
                    "uuid": record.uuid,
                    "identifier": record.identifier,
                    "updated": record.updated,
                }
            )
        return changed_records_data

    @property
    def information(self) -> Dict[str, Any]:
        return_dict = {}
        # records
        records_data = self.records_information
        if records_data:
            return_dict["records"] = records_data
        # members
        members_data = self.members_information
        if members_data:
            return_dict["members"] = members_data
        # questionnaires
        questionnaire_data = self.questionnaire_information
        if questionnaire_data:
            return_dict["questionnaires"] = questionnaire_data
        # changed records
        changed_records_data = self.changed_records_information
        if changed_records_data:
            return_dict["changed_records"] = changed_records_data
            # return
        return return_dict

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
    def get_dummy_user_private_key(dummy: "RlcUser") -> str:
        if settings.TESTING and dummy.email == "dummy@law-orga.de":
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

        if settings.TESTING and self.email == "dummy@law-orga.de":
            public_key = self.key["key"]["public_key"]
            private_key = RlcUser.get_dummy_user_private_key(self)
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

        ret: AsymmetricKey = key.key  # type: ignore
        return ret

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

    def lock(self) -> None:
        self.locked = True
        self.events.add(OrgUserLocked(org_user_uuid=self.uuid, org_pk=self.org_id))

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

    def check_delete_is_safe(self):
        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
        folders = r.get_list(self.org_id)

        for folder in folders:
            if folder.has_access(self) and len(folder.keys) <= 3:
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
        from core.models import HasPermission

        return HasPermission.objects.filter(user=self, permission=permission).exists()

    def __has_as_group_member_permission(self, permission):
        groups = [group.pk for group in self.groups.all()]
        from core.models import HasPermission

        return HasPermission.objects.filter(
            group_has_permission__pk__in=groups, permission=permission
        ).exists()

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

    def fix_keys(self, by: "RlcUser"):
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

    def unlock(self, by: "RlcUser"):
        self.fix_keys(by)
        self.locked = False
        self.events.add(
            OrgUserUnlocked(
                org_user_uuid=self.uuid,
                by_org_user_uuid=by.uuid,
                org_pk=self.org_id,
            )
        )
