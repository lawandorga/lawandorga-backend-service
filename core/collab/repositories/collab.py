from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.collab.models.collab_document import CollabDocument
from core.folders.domain.repositories.folder import FolderRepository


class CollabRepository:
    def get_document(
        self, uuid: UUID, user: RlcUser, fr: FolderRepository
    ) -> CollabDocument:
        raise NotImplementedError()

    def save_document(
        self, document: CollabDocument, user: RlcUser, fr: FolderRepository
    ) -> None:
        raise NotImplementedError()

    def delete_document(self, document: CollabDocument, user: RlcUser) -> None:
        raise NotImplementedError()
