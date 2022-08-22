from django.db import models

from apps.core.models import UserProfile
from apps.core.rlc.models import Org
from apps.static.encryption import AESEncryption, EncryptedModelMixin

from .tag import Tag


class EncryptedRecord(EncryptedModelMixin, models.Model):
    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(
        UserProfile, related_name="encrypted_records", on_delete=models.CASCADE
    )
    from_rlc = models.ForeignKey(
        Org, related_name="encrypted_records", on_delete=models.CASCADE
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
            key: str = record_encryption.encrypted_key  # type: ignore
        elif aes_key and user is None and private_key_user is None:
            key: str = aes_key  # type: ignore
        else:
            raise ValueError(
                "You have to set (user and private_key_user) or (aes_key)."
            )
        super().encrypt(key)

    def decrypt(self, user: UserProfile = None, private_key_user: str = None) -> None:  # type: ignore
        if user and private_key_user:
            key = self.get_decryption_key(user, private_key_user)
        else:
            raise ValueError("You have to set (user and private_key_user).")
        super().decrypt(key)

    def get_decryption_key(self, user: UserProfile, users_private_key: str) -> bytes:
        encryption = self.encryptions.get(user=user)
        encryption.decrypt(users_private_key)
        key = encryption.encrypted_key
        return key
