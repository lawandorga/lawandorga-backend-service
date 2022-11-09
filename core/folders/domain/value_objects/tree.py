from typing import Union
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.types import StrDict

FolderTreeType = list[tuple[StrDict, "FolderTreeType"]]


class FolderTree:
    def __init__(self, folders: list[Folder]):

        parent_dict: dict[Union[UUID, None], list[Folder]] = {}
        for f in folders:
            if f.parent_pk in parent_dict:
                parent_dict[f.parent_pk].append(f)
            else:
                parent_dict[f.parent_pk] = [f]

        def get_children(f: Folder):
            if f.pk not in parent_dict:
                return []
            folder_list = parent_dict.pop(f.pk)
            children = []
            for child in folder_list:
                node = (child.__dict__(), get_children(child))
                children.append(node)
            return children

        tree: FolderTreeType = []
        for folder in parent_dict[None]:
            root_node = (folder.__dict__(), get_children(folder))
            tree.append(root_node)
        self.__tree = tree

    def __dict__(self):
        return self.__tree
