from uuid import UUID, uuid4

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.symmetric_key import SymmetricKey

from seedwork.types import JsonDict


class Document:
    @classmethod
    def create(cls, text: str, user: str) -> "Document":
        return Document(text=text, user=user, uuid=uuid4())

    def __init__(self, text: str, user: str, uuid: UUID) -> None:
        self._text = text
        self._user = user
        self._uuid = uuid

    def __repr__(self) -> str:
        return "Document({}, {}, {})".format(self._text, self._user, self._uuid)

    @property
    def uuid(self):
        return self._uuid

    @property
    def text(self):
        return self._text

    def encrypt(self, key: SymmetricKey) -> "EncryptedDocument":
        return EncryptedDocument.create_from_document(self, key)


class EncryptedDocument:
    @classmethod
    def create_from_document(
        cls, document: Document, key: SymmetricKey
    ) -> "EncryptedDocument":
        open_box = OpenBox.create_from_str(document._text)
        locked_box = key.lock(open_box)
        return cls(enc_text=locked_box, user=document._user, uuid=document._uuid)

    @classmethod
    def create_from_dict(cls, d: JsonDict) -> "EncryptedDocument":
        assert (
            "user" in d
            and "text" in d
            and "uuid" in d
            and isinstance(d["uuid"], str)
            and isinstance(d["user"], str)
            and isinstance(d["text"], dict)
        )
        user = d["user"]
        locked_box = LockedBox.create_from_dict(d["text"])
        uuid = UUID(d["uuid"])
        return cls(enc_text=locked_box, user=user, uuid=uuid)

    def __init__(self, enc_text: LockedBox, user: str, uuid: UUID) -> None:
        self._enc_text = enc_text
        self._user = user
        self._uuid = uuid

    def as_dict(self) -> dict:
        return {
            "user": self._user,
            "uuid": str(self._uuid),
            "text": self._enc_text.as_dict(),
        }

    def decrypt(self, key: SymmetricKey) -> Document:
        box = key.unlock(self._enc_text)
        return Document(text=box.value_as_str, user=self._user, uuid=self._uuid)
