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
from django.db.models import Q

from backend.api.errors import CustomError
from backend.api.models import Rlc, UserProfile
from backend.recordmanagement.models import RecordTag
from backend.static.error_codes import ERROR__RECORD__KEY__RECORD_ENCRYPTION_NOT_FOUND
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC


class EncryptedRecordManager(models.Manager):
    def get_queryset(self):
        return EncryptedRecordQuerySet(self.model, using=self._db)

    def get_full_access_e_records(self, user):
        return self.get_queryset().get_full_access_e_records(user)

    def get_no_access_e_records(self, user):
        return self.get_queryset().get_no_access_e_records(user)

    def filter_by_rlc(self, rlc):
        return self.get_queryset().filter_by_rlc(rlc)


class EncryptedRecordQuerySet(models.QuerySet):
    def get_full_access_e_records(self, user):
        from backend.recordmanagement.models import EncryptedRecordPermission
        permissions = EncryptedRecordPermission.objects.filter(request_from=user, state='gr')

        return self.filter(Q(id__in=user.working_on_e_record.values_list('id', flat=True)) | Q(
            id__in=permissions.values_list('record_id', flat=True)))

    def get_no_access_e_records(self, user):
        has_perm = self.get_full_access_records(user)
        return self.exclude(id__in=has_perm.values_list('id', flat=True))

    def filter_by_rlc(self, rlc):
        """
        filters by the instance of the given rlc
        :param rlc: instance of rlc
        :return: filtered values
        """
        return self.filter(from_rlc=rlc)


class EncryptedRecord(models.Model):
    creator = models.ForeignKey(
        UserProfile, related_name="e_records_created", on_delete=models.SET_NULL, null=True)
    from_rlc = models.ForeignKey(Rlc, related_name='e_record_from_rlc', on_delete=models.SET_NULL, null=True,
                                 default=None)

    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    client = models.ForeignKey(
        'EncryptedClient', related_name="e_records", on_delete=models.SET_NULL, null=True)

    first_contact_date = models.DateField(default=None, null=True)
    last_contact_date = models.DateTimeField(default=None, null=True)
    first_consultation = models.DateTimeField(default=None, null=True)

    record_token = models.CharField(
        max_length=50, unique=True)

    official_note = models.TextField(blank=True, null=True)

    working_on_record = models.ManyToManyField(
        UserProfile, related_name="working_on_e_record", blank=True)
    tagged = models.ManyToManyField(RecordTag, related_name="e_tagged", blank=True)

    record_states_possible = (
        ('op', 'open'),
        ('cl', 'closed'),
        ('wa', 'waiting'),
        ('wo', 'working')
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

    objects = EncryptedRecordManager()

    def __str__(self):
        return 'e_record: ' + str(self.id) + ':' + self.record_token

    @staticmethod
    def unencrypted_changeable_fields():
        return ['official_note', 'state', 'record_token']

    @staticmethod
    def encrypted_changeable_fields():
        return ['note', 'consultant_team', 'lawyer', 'related_persons',
                'contact', 'bamf_token', 'foreign_token', 'first_correspondence',
                'circumstances', 'next_steps', 'status_described', 'additional_facts']

    @staticmethod
    def changeable_datetime_fields():
        return ['last_contact_date', 'first_contact_date', 'first_consultation']

    @staticmethod
    def ignore_fields():
        return ['id', 'client', 'from_rlc', 'created_on', 'last_edited']

    @staticmethod
    def specific_changed_fields():
        return ['working_on_record', 'tagged']

    @staticmethod
    def allowed_fields():
        return EncryptedRecord.changeable_datetime_fields() + EncryptedRecord.ignore_fields() + \
               EncryptedRecord.unencrypted_changeable_fields() + EncryptedRecord.encrypted_changeable_fields() + \
               EncryptedRecord.specific_changed_fields()

    def user_has_permission(self, user):
        """
        return if the user has permission edit and view the record in full detail
        :param user: user object, the user to check
        :return: boolean, true if the user has permission
        """
        from backend.recordmanagement.models import EncryptedRecordPermission
        return self.working_on_record.filter(id=user.id).count() == 1 or \
               EncryptedRecordPermission.objects.filter(record=self, request_from=user, state='gr').count() == 1 or \
               user.has_permission(PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc)

    def get_notification_emails(self):
        from backend.recordmanagement.models import EncryptedRecordPermission
        emails = []
        for user in list(self.working_on_record.all()):
            emails.append(user.email)
        for permission_request in list(EncryptedRecordPermission.objects.filter(record=self, state='gr')):
            emails.append(permission_request.request_from.email)
        return emails

    def get_notification_users(self) -> [UserProfile]:
        from backend.recordmanagement.models import EncryptedRecordPermission
        users = []
        for user in list(self.working_on_record.all()):
            users.append(user)
        for permission_request in list(EncryptedRecordPermission.objects.filter(record=self, state='gr')):
            users.append(permission_request.request_from)
        return users

    def get_users_with_permission(self) -> [UserProfile]:
        from backend.api.models import UserProfile, Permission
        working_on_users = self.working_on_record.all()
        users_with_record_permission = UserProfile.objects.filter(e_record_permissions_requested__record=self,
                                                                  e_record_permissions_requested__state='gr')
        users_with_overall_permission = Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC).get_real_users_with_permission_for_rlc(
            self.from_rlc)
        return working_on_users.union(users_with_record_permission).union(users_with_overall_permission).distinct()

    def get_users_with_decryption_keys(self) -> [UserProfile]:
        from backend.api.models import UserProfile
        from backend.static.permissions import get_record_encryption_keys_permissions_strings
        working_on_users = self.working_on_record.all()
        users_with_record_permission = UserProfile.objects.filter(e_record_permissions_requested__record=self,
                                                                  e_record_permissions_requested__state='gr')

        users_with_decryption_key_permissions = UserProfile.objects.get_users_with_special_permissions(
            get_record_encryption_keys_permissions_strings(), for_rlc=self.from_rlc)

        return working_on_users.union(users_with_record_permission).union(
            users_with_decryption_key_permissions).distinct()

    def get_decryption_key(self, user: UserProfile, users_private_key: bytes) -> str:
        from backend.recordmanagement.models import RecordEncryption
        record_encryptions: [RecordEncryption] = RecordEncryption.objects.filter(user=user, record=self)
        result = None
        for encryption in record_encryptions:
            if result:
                encryption.delete()
                continue
            try:
                key = encryption.decrypt(users_private_key)
                result = key
            except:
                encryption.delete()
        if not result:
            raise CustomError(ERROR__RECORD__KEY__RECORD_ENCRYPTION_NOT_FOUND)
        return result
