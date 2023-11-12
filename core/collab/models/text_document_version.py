from django.db import models

from core.seedwork.encryption import AESEncryption, EncryptedModelMixin

from .collab_document import CollabDocument


class TextDocumentVersion(EncryptedModelMixin, models.Model):
    document = models.ForeignKey(
        CollabDocument, related_name="versions", on_delete=models.CASCADE
    )
    content = models.BinaryField(blank=True)
    quill = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    encrypted_fields = ["content"]
    encryption_class = AESEncryption

    class Meta:
        verbose_name = "TextDocumentVersion"
        verbose_name_plural = "TextDocumentVersions"

    def __str__(self):
        return "textDocumentVersion: {}; document: {};".format(
            self.pk, self.document.pk
        )

    def encrypt(self, aes_key_rlc=None, request=None):
        if aes_key_rlc:
            key = aes_key_rlc
        elif request:
            user = request.user
            private_key_user = user.get_private_key(request=request)
            key = user.rlc.get_aes_key(user=user, private_key_user=private_key_user)
        else:
            raise ValueError("You need to pass (aes_key_rlc) or (request).")
        super().encrypt(key)

    def decrypt(self, aes_key_rlc=None, user=None, private_key_user=None, request=None):
        if aes_key_rlc:
            key = aes_key_rlc
        elif user and private_key_user:
            key = user.rlc.get_aes_key(user=user, private_key_user=private_key_user)
        elif request:
            user = request.user
            private_key_user = user.get_private_key(request=request)
            key = user.rlc.get_aes_key(user=user, private_key_user=private_key_user)
        else:
            raise ValueError(
                "You need to pass (aes_key_rlc) or (user and private_key_user) or (request)."
            )
        super().decrypt(key)
