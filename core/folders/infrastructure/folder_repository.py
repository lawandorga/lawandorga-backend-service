from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.value_objects.tree import FolderTree
from core.folders.models import FoldersFolder


class DjangoFolderRepository(FolderRepository):
    @classmethod
    def find_key_owner(cls, slug: UUID) -> IOwner:
        return cast(IOwner, RlcUser.objects.get(slug=slug))

    @classmethod
    def retrieve(cls, org_pk: int, pk: UUID) -> Folder:
        return FoldersFolder.query().filter(org_pk=org_pk).get(pk=pk).to_domain()

    @classmethod
    def list(cls, org_pk: int) -> list[Folder]:
        return [
            f.to_domain() for f in list(FoldersFolder.query().filter(org_pk=org_pk))
        ]

    @classmethod
    def save(cls, folder: Folder):
        FoldersFolder.from_domain(folder).save()

    @classmethod
    def delete(cls, folder: Folder):
        FoldersFolder.from_domain(folder).delete()

    @classmethod
    def tree(cls, org_pk: int) -> FolderTree:
        pass
