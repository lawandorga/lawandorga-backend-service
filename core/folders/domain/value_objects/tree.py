from typing import Optional, Union
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.keys import FolderKey
from core.folders.domain.value_objects.keys.parent_key import ParentKey


class Access:
    def __init__(self, folders_dict: dict[UUID, Folder], folder: Folder):
        self.__folders_dict = folders_dict

        self.access = self.get_owners_with_access(folder)

    def get_owners_with_access(self, folder: Folder):
        access = []
        for key in folder.keys:
            if isinstance(key, FolderKey):
                access.append(
                    {"name": str(key.owner.name), "slug": str(key.owner.slug)}
                )
                continue
            if isinstance(key, ParentKey):
                if not folder.stop_inherit:
                    f = self.__folders_dict[folder.parent_pk]
                    access += self.get_owners_with_access(f)
                continue
            access.append({"name": "Unknown", "slug": "-"})
        return access

    def as_dict(self) -> list[StrDict]:
        return self.access


class Node:
    def __init__(
        self,
        folders_dict: dict[UUID, Folder],
        parent_dict: dict[Optional[UUID], list[Folder]],
        folder: Folder,
    ):
        self.__folders_dict = folders_dict
        self.__parent_dict = parent_dict

        self.folder = folder
        self.children = self.get_children(folder)
        self.content = folder.content
        self.access = Access(folders_dict, folder)

    def get_children(self, folder) -> list["Node"]:
        if folder.pk not in self.__parent_dict:
            return []

        folder_list = self.__parent_dict[folder.pk]

        children = []
        for child in folder_list:
            node = Node(
                folders_dict=self.__folders_dict,
                parent_dict=self.__parent_dict,
                folder=child,
            )
            children.append(node)
        return children

    def as_dict(self):
        return {
            "folder": self.folder.as_dict(),
            "children": [child.as_dict() for child in self.children],
            "content": self.folder.content,
            "access": self.access.as_dict(),
        }


class FolderTree:
    def __init__(self, folders: list[Folder]):
        self.folders = folders

        if len(folders) == 0:
            self.__tree = []
            return

        folders_dict = self.__generate_folders_dict()
        parent_dict = self.__generate_parent_dict()

        tree = []
        for folder in parent_dict[None]:
            root_node = Node(folders_dict, parent_dict, folder)
            tree.append(root_node.as_dict())

        self.__tree = tree

    def __generate_folders_dict(self) -> dict[UUID, Folder]:
        folders_dict = {f.pk: f for f in self.folders}
        return folders_dict

    def __generate_parent_dict(self) -> dict[Optional[UUID], list[Folder]]:
        parent_dict: dict[Union[UUID, None], list[Folder]] = {}
        for i in self.folders:
            if i.parent_pk not in parent_dict:
                parent_dict[i.parent_pk] = []
            parent_dict[i.parent_pk].append(i)
        return parent_dict

    def as_dict(self):
        return self.__tree
