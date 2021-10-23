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
from django.utils import timezone
from apps.api.models import UserProfile
from apps.collab.models import TextDocument
from apps.static.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption


class TextDocumentVersion(
    EncryptedModelMixin, models.Model,
):
    document = models.ForeignKey(
        TextDocument, related_name="versions", null=False, on_delete=models.CASCADE
    )
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(
        UserProfile,
        related_name="text_document_versions_created",
        on_delete=models.SET_NULL,
        null=True,
    )

    is_draft = models.BooleanField(default=True)
    content = models.BinaryField()

    encrypted_fields = ["content"]
    encryption_class = AESEncryption

    # @staticmethod
    # def create(
    #     content: str,
    #     is_draft: bool,
    #     aes_key: str,
    #     user: UserProfile,
    #     document: TextDocument,
    # ) -> "TextDocumentVersion":
    #     encrypted_content = AESEncryption.encrypt(content, aes_key)
    #     version = TextDocumentVersion(
    #         is_draft=is_draft,
    #         content=encrypted_content,
    #         creator=user,
    #         document=document,
    #     )
    #     version.save()
    #
    #     document.last_editor = user
    #     document.last_edited = timezone.now()
    #     document.save()
    #
    #     return version

    def encrypt(self, rlc_aes_key: bytes) -> None:
        super().encrypt(rlc_aes_key)

    def decrypt(self, private_key_rlc: str = None) -> None:
        super().decrypt(private_key_rlc)
