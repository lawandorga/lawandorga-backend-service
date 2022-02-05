from apps.static.encryption import AESEncryption, EncryptedModelMixin
from apps.collab.models.collab_document import CollabDocument
from apps.api.models import UserProfile
from django.db import models


class TextDocumentVersion(EncryptedModelMixin, models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    document = models.ForeignKey(CollabDocument, related_name="versions", on_delete=models.CASCADE)
    creator = models.ForeignKey(UserProfile, related_name="text_document_versions_created", on_delete=models.SET_NULL,
                                null=True, blank=True)
    is_draft = models.BooleanField(default=True)
    content = models.BinaryField(blank=True)
    quill = models.BooleanField(default=True)

    encrypted_fields = ["content"]
    encryption_class = AESEncryption

    class Meta:
        verbose_name = 'TextDocumentVersion'
        verbose_name_plural = 'TextDocumentVersions'

    def __str__(self):
        return 'textDocumentVersion: {}; document: {};'.format(self.id, self.document.id)

    def encrypt(self, aes_key_rlc=None):
        if aes_key_rlc:
            key = aes_key_rlc
        else:
            raise ValueError('You need to pass (aes_key_rlc).')
        super().encrypt(key)

    def decrypt(self, aes_key_rlc=None):
        if aes_key_rlc:
            key = aes_key_rlc
        else:
            raise ValueError('You need to pass (aes_key_rlc).')
        super().decrypt(key)
