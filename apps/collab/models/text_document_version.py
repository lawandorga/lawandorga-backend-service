from apps.static.encryption import AESEncryption, EncryptedModelMixin
from apps.collab.models import TextDocument
from apps.api.models import UserProfile
from django.db import models


class TextDocumentVersion(EncryptedModelMixin, models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    document = models.ForeignKey(TextDocument, related_name="versions", null=False, on_delete=models.CASCADE)
    creator = models.ForeignKey(UserProfile, related_name="text_document_versions_created", on_delete=models.SET_NULL,
                                null=True)
    is_draft = models.BooleanField(default=True)
    content = models.BinaryField()
    quill = models.BooleanField(default=True)

    encrypted_fields = ["content"]
    encryption_class = AESEncryption

    def encrypt(self, aes_key_rlc: bytes) -> None:
        super().encrypt(aes_key_rlc)

    def decrypt(self, aes_key_rlc: str = None) -> None:
        super().decrypt(aes_key_rlc)
