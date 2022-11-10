from typing import cast
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.value_objects.tree import FolderTree
from core.folders.models import FoldersFolder


class DjangoFolderRepository(FolderRepository):
    @classmethod
    def __as_dict(cls, org_pk: int) -> dict[UUID, FoldersFolder]:
        folders = {}
        for f in list(FoldersFolder.query().filter(org_pk=org_pk)):
            folders[f.pk] = f
        return folders

    @classmethod
    def find_key_owner(cls, slug: UUID) -> IOwner:
        return cast(IOwner, RlcUser.objects.get(slug=slug))

    @classmethod
    def retrieve(cls, org_pk: int, pk: UUID) -> Folder:
        folders = cls.__as_dict(org_pk)
        if pk in folders:
            return folders[pk].to_domain(folders)
        raise ObjectDoesNotExist()

    @classmethod
    def list(cls, org_pk: int) -> list[Folder]:
        folders = cls.__as_dict(org_pk)
        folders_list = []
        for folder in folders.values():
            folders_list.append(folder.to_domain(folders))
        return folders_list

    @classmethod
    def save(cls, folder: Folder):
        FoldersFolder.from_domain(folder).save()

    @classmethod
    def delete(cls, folder: Folder):
        FoldersFolder.from_domain(folder).delete()

    @classmethod
    def tree(cls, org_pk: int) -> FolderTree:
        return FolderTree(cls.list(org_pk))
