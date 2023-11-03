from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.folder_key import EncryptedFolderKeyOfUser
from core.folders.domain.value_objects.parent_key import ParentKey

from seedwork.types import JsonDict

if TYPE_CHECKING:
    from core.auth.models.org_user import RlcUser


class TreeAccess:
    def __init__(self, folders_dict: dict[UUID, Folder], folder: Folder):
        self.__folders_dict = folders_dict

        self.access = self.get_owners_with_access(folder)

    def get_owners_with_access(self, folder: Folder, source="direct"):
        access = []
        for key in folder.keys:
            if isinstance(key, EncryptedFolderKeyOfUser):
                access.append(
                    {
                        "name": str(key.owner_uuid),  # TODO: change to name
                        "uuid": str(key.owner_uuid),
                        "is_valid": key.is_valid,
                        "source": source,
                        "actions": self.get_actions(folder, key, source),
                    }
                )
                continue
            if isinstance(key, ParentKey):
                if not folder.stop_inherit:
                    assert folder.parent_uuid is not None
                    f = self.__folders_dict[folder.parent_uuid]
                    access += self.get_owners_with_access(f, "parent")
                continue
            raise ValueError("Unknown type of key.")
        return access

    def get_actions(self, folder, key, source):
        if source == "direct":
            url = "/folders/folders/{}/revoke_access/".format(folder.uuid)
            return {"REVOKE_ACCESS": {"url": url, "user_uuid": key.owner_uuid}}
        return {}

    def as_dict(self) -> list[JsonDict]:
        return self.access


class TreeFolder:
    def __init__(self, folder: Folder):
        self.__folder = folder

    def get_actions(self, has_access: bool):
        if has_access:
            return {"OPEN": {"uuid": self.__folder.uuid}}
        return {}

    def as_dict(self, user: "RlcUser") -> JsonDict:
        data = self.__folder.as_dict()
        has_access = self.__folder.has_access(user)
        data["has_access"] = has_access
        data["actions"] = self.get_actions(has_access)
        return data


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
        self.content = folder.items
        self.access = TreeAccess(folders_dict, folder)

    def get_children(self, folder) -> list["Node"]:
        if folder.uuid not in self.__parent_dict:
            return []

        folder_list = self.__parent_dict[folder.uuid]

        children = []
        for child in folder_list:
            node = Node(
                folders_dict=self.__folders_dict,
                parent_dict=self.__parent_dict,
                folder=child,
            )
            children.append(node)
        return children

    def as_dict(self, user: "RlcUser"):
        return {
            "folder": TreeFolder(self.folder).as_dict(user),
            "children": [child.as_dict(user) for child in self.children],
            "content": self.folder.items if self.folder.has_access(user) else [],
            "access": self.access.as_dict(),
        }


class FolderTree:
    def __init__(self, user: "RlcUser", folders: list[Folder]):
        self.folders = folders
        self.user = user

        if len(folders) == 0:
            self.__tree = []
            return

        folders_dict = self.__generate_folders_dict()
        parent_dict = self.__generate_parent_dict()

        tree = []
        for folder in parent_dict[None]:
            root_node = Node(folders_dict, parent_dict, folder)
            tree.append(root_node.as_dict(self.user))

        self.__tree = tree

    def __generate_folders_dict(self) -> dict[UUID, Folder]:
        folders_dict = {f.uuid: f for f in self.folders}
        return folders_dict

    def __generate_parent_dict(self) -> dict[Optional[UUID], list[Folder]]:
        parent_dict: dict[Union[UUID, None], list[Folder]] = {}
        for i in self.folders:
            if i.parent_uuid not in parent_dict:
                parent_dict[i.parent_uuid] = []
            parent_dict[i.parent_uuid].append(i)
        return parent_dict

    def as_dict(self):
        return self.__tree
