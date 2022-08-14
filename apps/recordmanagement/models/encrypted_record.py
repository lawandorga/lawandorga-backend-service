# type: ignore
from django.db import models

from apps.core.models import UserProfile
from apps.core.models.rlc import Rlc
from apps.core.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from apps.static.encryption import AESEncryption, EncryptedModelMixin

from .tag import Tag


class EncryptedRecord(EncryptedModelMixin, models.Model):
    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

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
    record_token = models.CharField(max_length=50)
    official_note = models.TextField(blank=True, null=True)
    working_on_record = models.ManyToManyField(
        UserProfile, related_name="working_on_e_record"
    )
    tags = models.ManyToManyField(Tag, related_name="records")

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

    # TODO: unique together with record token and rlc

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

    class Meta:
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self):
        return "record: {}; token: {};".format(self.pk, self.record_token)

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
        from apps.recordmanagement.models.encrypted_record_permission import (
            RecordAccess,
        )

        return (
            self.working_on_record.filter(id=user.id).count() == 1
            or RecordAccess.objects.filter(
                record=self, request_from=user, state="gr"
            ).count()
            == 1
            or user.has_permission(
                PERMISSION_RECORDS_ACCESS_ALL_RECORDS, for_rlc=self.from_rlc
            )
        )

    def get_notification_emails(self):
        emails = []
        for user in list(self.working_on_record.all()):
            emails.append(user.email)
        from apps.recordmanagement.models.encrypted_record_permission import (
            RecordAccess,
        )

        for permission_request in list(
            RecordAccess.objects.filter(record=self, state="gr")
        ):
            emails.append(permission_request.request_from.email)
        return emails

    def get_notification_users(self) -> [UserProfile]:

        users = []
        for user in list(self.working_on_record.all()):
            users.append(user)
        from apps.recordmanagement.models.encrypted_record_permission import (
            RecordAccess,
        )

        for permission_request in RecordAccess.objects.filter(record=self, state="gr"):
            users.append(permission_request.request_from)
        return users

    def get_decryption_key(self, user: UserProfile, users_private_key: str) -> str:
        encryption = self.encryptions.get(user=user)
        encryption.decrypt(users_private_key)
        key = encryption.encrypted_key
        return key
