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
from backend.recordmanagement.models import RecordTag
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
from backend.static.encryption import AESEncryption, EncryptedModelMixin
from django_prometheus.models import ExportModelOperationsMixin
from backend.api.models.rlc import Rlc
from backend.api.models import UserProfile
from django.db import models


class EncryptedRecord(
    ExportModelOperationsMixin("encrypted_record"), EncryptedModelMixin, models.Model
):
    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(
        UserProfile, related_name="encrypted_records", on_delete=models.CASCADE
    )
    from_rlc = models.ForeignKey(
        Rlc, related_name="encrypted_records", on_delete=models.CASCADE
    )
    client = models.ForeignKey(
        "EncryptedClient", related_name="e_records", on_delete=models.CASCADE
    )

    first_contact_date = models.DateField(default=None, null=True)
    last_contact_date = models.DateTimeField(default=None, null=True)
    first_consultation = models.DateTimeField(default=None, null=True)
    record_token = models.CharField(max_length=50, unique=True)
    official_note = models.TextField(blank=True, null=True)
    working_on_record = models.ManyToManyField(
        UserProfile, related_name="working_on_e_record"
    )
    tagged = models.ManyToManyField(RecordTag, related_name="e_tagged")

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
    encrypted_fields = [
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

    def __str__(self):
        return "e_record: " + str(self.id) + ":" + self.record_token

    def encrypt(
        self,
        user: UserProfile = None,
        private_key_user: bytes = None,
        aes_key: str = None,
    ) -> None:
        if user and private_key_user and aes_key is None:
            record_encryption = self.encryptions.get(user=user)
            record_encryption.decrypt(private_key_user)
            key = record_encryption.encrypted_key
        elif aes_key and user is None and private_key_user is None:
            key = aes_key
        else:
            raise ValueError(
                "You have to set (user and private_key_user) or (aes_key)."
            )
        super().encrypt(key)

    def decrypt(self, user: UserProfile = None, private_key_user: str = None) -> None:
        if user and private_key_user:
            key = self.get_decryption_key(user, private_key_user)
        else:
            raise ValueError("You have to set (user and private_key_user).")
        super().decrypt(key)

    def user_has_permission(self, user):
        """
        return if the user has permission edit and view the record in full detail
        :param user: user object, the user to check
        :return: boolean, true if the user has permission
        """
        from backend.recordmanagement.models.encrypted_record_permission import (
            EncryptedRecordPermission,
        )

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
        from backend.recordmanagement.models.encrypted_record_permission import (
            EncryptedRecordPermission,
        )

        for permission_request in list(
            EncryptedRecordPermission.objects.filter(record=self, state="gr")
        ):
            emails.append(permission_request.request_from.email)
        return emails

    def get_notification_users(self) -> [UserProfile]:

        users = []
        for user in list(self.working_on_record.all()):
            users.append(user)
        from backend.recordmanagement.models.encrypted_record_permission import (
            EncryptedRecordPermission,
        )

        for permission_request in EncryptedRecordPermission.objects.filter(
            record=self, state="gr"
        ):
            users.append(permission_request.request_from)
        return users

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

    def get_decryption_key(self, user: UserProfile, users_private_key: str) -> str:
        encryption = self.encryptions.get(user=user)
        encryption.decrypt(users_private_key)
        key = encryption.encrypted_key
        return key
