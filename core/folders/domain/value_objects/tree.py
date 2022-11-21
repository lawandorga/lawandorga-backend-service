from typing import TypedDict, Union
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.types import StrDict


class Node(TypedDict):
    folder: StrDict
    children: list["Node"]


Tree = list[Node]


class FolderTree:
    def __init__(self, folders: list[Folder]):

        if len(folders) == 0:
            self.__tree = []
            return

        parent_dict: dict[Union[UUID, None], list[Folder]] = {}
        for i in folders:
            if i.parent_pk in parent_dict:
                parent_dict[i.parent_pk].append(i)
            else:
                parent_dict[i.parent_pk] = [i]

        def build_node(f, c):
            return {"folder": f.__dict__(), "children": c, "content": f.content}

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
