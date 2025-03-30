from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.collab import Collab
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.domain.repositories.item import ItemRepository


class CollabRepository(ItemRepository):
    IDENTIFIER = Collab.REPOSITORY

    def retrieve(self, uuid: UUID, org_pk: int) -> Collab:
        return Collab.objects.filter(org_id=org_pk).get(uuid=uuid)

    def get_document(self, uuid: UUID, user: OrgUser, fr: FolderRepository) -> Collab:
        collab = Collab.objects.filter(org_id=user.org_id).get(uuid=uuid)
        folder = fr.retrieve(org_pk=user.org_id, uuid=collab.folder_uuid)
        collab._decrypt(folder=folder, user=user)
        return collab

    def save_document(self, collab: Collab, user: OrgUser, folder: Folder) -> None:
        assert folder.uuid == collab.folder_uuid, "folder uuid mismatch"
        collab._encrypt(folder=folder, user=user)
        collab.save(__allow=True)

    def delete_document(self, uuid: UUID, user: OrgUser) -> None:
        collab = Collab.objects.filter(org_id=user.org_id).get(uuid=uuid)
        collab.delete()

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        _org_id = org_pk if org_pk else 0
        Collab.objects.filter(folder_uuid=folder_uuid, org_id=_org_id).delete()
