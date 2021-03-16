#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from django.db import models
from datetime import datetime
import pytz
from django_prometheus.models import ExportModelOperationsMixin

from backend.api.errors import CustomError
from backend.api.models import UserProfile
from backend.api.models.rlc import Rlc
from backend.recordmanagement.models.record_tag import RecordTag
from backend.static import error_codes
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
from backend.static.date_utils import parse_date
from backend.static.encryption import AESEncryption, EncryptedModelMixin
from backend.static import permissions


class EncryptedRecordManager(models.Manager):
    def get_queryset(self):
        return EncryptedRecordQuerySet(self.model, using=self._db)

    def filter_by_rlc(self, rlc):
        """
        filters records by rlc
        :param rlc:
        :return:
        """
        return self.get_queryset().filter_by_rlc(rlc)

    def get_record(self, user: UserProfile, id) -> "EncryptedRecord":
        if not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_RLC, for_rlc=user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        try:
            e_record: EncryptedRecord = EncryptedRecord.objects.get(pk=int(id))
        except Exception as e:
            raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)
        if user.rlc != e_record.from_rlc:
            raise CustomError(error_codes.ERROR__API__WRONG_RLC)

        return e_record


class EncryptedRecordQuerySet(models.QuerySet):
    def filter_by_rlc(self, rlc):
        """
        filters by the instance of the given rlc
        :param rlc: instance of rlc
        :return: filtered values
        """
        return self.filter(from_rlc=rlc)


class EncryptedRecord(ExportModelOperationsMixin("encrypted_record"), EncryptedModelMixin, models.Model):
    creator = models.ForeignKey(
        UserProfile,
        related_name="encrypted_records",
        on_delete=models.SET_NULL,
        null=True,
    )
    from_rlc = models.ForeignKey(
        Rlc,
        related_name="encrypted_records",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )

    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    client = models.ForeignKey(
        "EncryptedClient",
        related_name="e_records",
        on_delete=models.SET_NULL,
        null=True,
    )

    first_contact_date = models.DateField(default=None, null=True)
    last_contact_date = models.DateTimeField(default=None, null=True)
    first_consultation = models.DateTimeField(default=None, null=True)

    record_token = models.CharField(max_length=50, unique=True)

    official_note = models.TextField(blank=True, null=True)

    working_on_record = models.ManyToManyField(
        UserProfile, related_name="working_on_e_record", blank=True
    )
    tagged = models.ManyToManyField(RecordTag, related_name="e_tagged", blank=True)

    record_states_possible = (
        ("op", "open"),
        ("cl", "closed"),
        ("wa", "waiting"),
        ("wo", "working"),
    )

    state = models.CharField(max_length=2, choices=record_states_possible)

    # encrypted
    note = models.BinaryField()
    consultant_team = models.BinaryField()
    lawyer = models.BinaryField()
    related_persons = models.BinaryField()
    contact = models.BinaryField()

    bamf_token = models.BinaryField()
    foreign_token = models.BinaryField()

    first_correspondence = models.BinaryField()
    circumstances = models.BinaryField()
    next_steps = models.BinaryField()
    status_described = models.BinaryField()
    additional_facts = models.BinaryField()

    encryption_class = AESEncryption
    encrypted_fields = ["note", "consultant_team", "lawyer", "related_persons", "contact", "bamf_token",
                        "foreign_token", "first_correspondence", "circumstances", "next_steps", "status_described",
                        "additional_facts"]

    objects = EncryptedRecordManager()

    def __str__(self):
        return "e_record: " + str(self.id) + ":" + self.record_token

    def encrypt(self, user: UserProfile = None, private_key_user: bytes = None, aes_key: str = None) -> None:
        if user and private_key_user:
            record_encryption = self.encryptions.get(user=user)
            record_encryption.decrypt(private_key_user)
            key = record_encryption.encrypted_key
        elif aes_key:
            key = aes_key
        else:
            raise ValueError('You have to set (user and private_key_user) or (aes_key).')
        super().encrypt(key)

    def decrypt(self, user: UserProfile = None, private_key_user: str = None) -> None:
        if user and private_key_user:
            encryption = self.encryptions.get(user=user)
            encryption.decrypt(private_key_user)
            key = encryption.encrypted_key
        else:
            raise ValueError('You have to set (user and private_key_user).')
        super().decrypt(key)

    def patch(self, record_data, record_key: str) -> [str]:
        """
        patches record from object, updating last_edited
        :param record_data: object containing only fields of record with new values
        :param record_key: record encryption key
        :return: array containing names of fields which were patched
        """
        unpatchable_fields = self.ignore_fields()
        unencrypted_changeable_fields = self.unencrypted_changeable_fields()
        changeable_datetime_fields = self.changeable_datetime_fields()

        new_tags = []
        patched = []
        for key, value in record_data.items():
            if key not in self.allowed_fields():
                raise CustomError(error_codes.ERROR__API__FIELD_NOT_ALLOWED)

            if key in unpatchable_fields:
                continue
            elif key == "tagged":
                if record_data[key].__len__() == 0:
                    raise CustomError(error_codes.ERROR__RECORD__TAG__AT_LEAST_ONE)
                for tag_id in record_data[key]:
                    try:
                        tag: RecordTag = RecordTag.objects.get(pk=tag_id)
                    except Exception as e:
                        raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)
                    new_tags.append(tag)
            elif key == "working_on_record":
                pass
            else:
                patched.append(key)
                if key in unencrypted_changeable_fields:
                    to_save = value
                elif key in changeable_datetime_fields:
                    to_save = parse_date(value)
                else:
                    to_save = AESEncryption.encrypt(value, record_key)
                setattr(self, key, to_save)

        if new_tags.__len__() > 0:
            patched.append("tagged")
            self.tagged.clear()
            for tag in new_tags:
                self.tagged.add(tag)

        self.last_edited = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.save()
        return patched

    @staticmethod
    def unencrypted_changeable_fields():
        return ["official_note", "state", "record_token"]

    @staticmethod
    def encrypted_changeable_fields():
        return [
            "note",
            "consultant_team",
            "lawyer",
            "related_persons",
            "contact",
            "bamf_token",
            "foreign_token",
            "first_correspondence",
            "circumstances",
            "next_steps",
            "status_described",
            "additional_facts",
        ]

    @staticmethod
    def changeable_datetime_fields():
        return ["last_contact_date", "first_contact_date", "first_consultation"]

    @staticmethod
    def ignore_fields():
        return [
            "id",
            "client",
            "from_rlc",
            "created_on",
            "last_edited",
            "from_rlc",
            "client",
        ]

    @staticmethod
    def specific_changed_fields():
        return ["working_on_record", "tagged"]

    @staticmethod
    def allowed_fields():
        return (
            EncryptedRecord.changeable_datetime_fields()
            + EncryptedRecord.ignore_fields()
            + EncryptedRecord.unencrypted_changeable_fields()
            + EncryptedRecord.encrypted_changeable_fields()
            + EncryptedRecord.specific_changed_fields()
        )

    def user_has_permission(self, user):
        """
        return if the user has permission edit and view the record in full detail
        :param user: user object, the user to check
        :return: boolean, true if the user has permission
        """

        from backend.recordmanagement.models.encrypted_record_permission import EncryptedRecordPermission
        return (
            self.working_on_record.filter(id=user.id).count() == 1
            or EncryptedRecordPermission.objects.filter(
                record=self, request_from=user, state="gr"
            ).count()
            == 1
            or user.has_permission(
                PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=self.from_rlc
            )
        )

    def get_notification_emails(self):

        emails = []
        for user in list(self.working_on_record.all()):
            emails.append(user.email)
        from backend.recordmanagement.models.encrypted_record_permission import EncryptedRecordPermission
        for permission_request in list(
            EncryptedRecordPermission.objects.filter(record=self, state="gr")
        ):
            emails.append(permission_request.request_from.email)
        return emails

    def get_notification_users(self) -> [UserProfile]:

        users = []
        for user in list(self.working_on_record.all()):
            users.append(user)
        from backend.recordmanagement.models.encrypted_record_permission import EncryptedRecordPermission
        for permission_request in EncryptedRecordPermission.objects.filter(
            record=self, state="gr"
        ):
            users.append(permission_request.request_from)
        return users

    def get_users_with_permission(self) -> [UserProfile]:
        from backend.api.models import UserProfile

        working_on_users = self.working_on_record.all()
        users_with_record_permission = UserProfile.objects.filter(
            e_record_permissions_requested__record=self,
            e_record_permissions_requested__state="gr",
        )
        from backend.api.models.permission import Permission
        users_with_overall_permission = Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
        ).get_real_users_with_permission_for_rlc(self.from_rlc)
        return (
            working_on_users.union(users_with_record_permission)
            .union(users_with_overall_permission)
            .distinct()
        )

    def get_users_with_decryption_keys(self) -> [UserProfile]:
        from backend.api.models import UserProfile
        from backend.static.permissions import (
            get_record_encryption_keys_permissions_strings,
        )

        working_on_users = self.working_on_record.all()
        users_with_record_permission = UserProfile.objects.filter(
            e_record_permissions_requested__record=self,
            e_record_permissions_requested__state="gr",
        )

        users_with_decryption_key_permissions = UserProfile.objects.get_users_with_special_permissions(
            get_record_encryption_keys_permissions_strings(), for_rlc=self.from_rlc
        )

        return (
            working_on_users.union(users_with_record_permission)
            .union(users_with_decryption_key_permissions)
            .distinct()
        )

    def get_decryption_key(self, user: UserProfile, users_private_key: bytes) -> str:


        from backend.recordmanagement.models.record_encryption import RecordEncryption
        record_encryptions: [RecordEncryption] = RecordEncryption.objects.filter(
            user=user, record=self
        )
        result = None
        for encryption in record_encryptions:
            if result:
                encryption.delete()
                continue
            try:
                encryption.decrypt(users_private_key)
                key = encryption.encrypted_key
                result = key
            except Exception as e:
                encryption.delete()
        if not result:
            raise CustomError(
                error_codes.ERROR__RECORD__KEY__RECORD_ENCRYPTION_NOT_FOUND
            )
        return result
