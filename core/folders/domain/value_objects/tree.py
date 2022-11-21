from typing import TypedDict, Union
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.keys import FolderKey
from core.folders.domain.value_objects.keys.parent_key import ParentKey


class Node(TypedDict):
    folder: StrDict
    children: list["Node"]


Tree = list[Node]


class FolderTree:
    def __init__(self, folders: list[Folder]):

        if len(folders) == 0:
            self.__tree = []
            return

        folders_dict = {f.pk: f for f in folders}

        parent_dict: dict[Union[UUID, None], list[Folder]] = {}
        for i in folders:
            if i.parent_pk in parent_dict:
                parent_dict[i.parent_pk].append(i)
            else:
                parent_dict[i.parent_pk] = [i]

        def get_owners_with_access(folder: Folder):
            access = []
            for key in folder.keys:
                if isinstance(key, FolderKey):
                    access.append(key.owner.name)
                    continue
                if isinstance(key, ParentKey):
                    f = folders_dict[folder.parent_pk]
                    access += get_owners_with_access(f)
                    continue
                access.append("Unknown")
            return access

        def build_node(f: Folder, c):
            return {
                "folder": f.__dict__(),
                "children": c,
                "content": f.content,
                "access": get_owners_with_access(f),
            }

        def get_children(f: Folder):
            if f.pk not in parent_dict:
                return []
            folder_list = parent_dict.pop(f.pk)
            children = []
            for child in folder_list:
                node = build_node(child, get_children(child))
                children.append(node)
            return children

        tree: Tree = []
        for folder in parent_dict[None]:
            root_node = build_node(folder, get_children(folder))
            tree.append(root_node)

        self.__tree = tree

    def __dict__(self):
        return self.__tree
