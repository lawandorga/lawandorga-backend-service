from typing import Optional, TypedDict, cast
from uuid import UUID

from django.db import transaction
from pydantic import BaseModel, ConfigDict

from core.auth.models import RlcUser
from core.data_sheets.models import DataSheet
from core.folders.api import schemas
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository
from core.folders.use_cases.folder import get_repository
from core.rlc.models.group import Group
from core.seedwork.api_layer import Router
from core.seedwork.repository import RepositoryWarehouse

router = Router()


class OutputContent(BaseModel):
    uuid: UUID
    name: Optional[str]
    repository: str

    model_config = ConfigDict(from_attributes=True)


class OutputAccess(BaseModel):
    name: str
    uuid: Optional[UUID]
    source: str
    actions: list[str]

    model_config = ConfigDict(from_attributes=True)


class OutputTreeFolder(BaseModel):
    name: str
    uuid: UUID
    stop_inherit: bool
    has_access: bool
    actions: list[str]


class OutputFolderTreeNode(BaseModel):
    folder: OutputTreeFolder
    children: list["OutputFolderTreeNode"]
    content: list[OutputContent]
    access: list[OutputAccess]
    group_access: list[OutputAccess]


class OutputPerson(BaseModel):
    name: str
    uuid: UUID

    model_config = ConfigDict(from_attributes=True)


class OutputGroup(BaseModel):
    name: str
    uuid: UUID

    model_config = ConfigDict(from_attributes=True)


class OutputFolderPage(BaseModel):
    tree: list[OutputFolderTreeNode]
    available_persons: list[OutputPerson]
    available_groups: list[OutputGroup]


class Context(TypedDict):
    available_users: list[RlcUser]
    available_groups: list[Group]
    folders: list[Folder]
    folders_dict: dict[UUID, Folder]
    parent_dict: dict[Optional[UUID], list[Folder]]
    users_dict: dict[UUID, RlcUser]
    groups_dict: dict[UUID, Group]


class ContextBuilder:
    def __init__(self) -> None:
        self.context: Context = {
            "available_users": [],
            "available_groups": [],
            "folders": [],
            "folders_dict": {},
            "parent_dict": {},
            "users_dict": {},
            "groups_dict": {},
        }

    def build_available_users(self, org_id: int):
        x = list(RlcUser.objects.filter(org_id=org_id))
        self.context["available_users"] = x
        return self

    def build_available_groups(self, org_id: int):
        x = list(Group.objects.filter(from_rlc_id=org_id))
        self.context["available_groups"] = x
        return self

    def build_folders(self, org_id: int):
        r = get_repository()
        x = r.get_list(org_id)
        self.context["folders"] = x
        return self

    def build_folder_dicts(self):
        folders_dict = {}
        parent_dict = {}
        for folder in self.context["folders"]:
            folders_dict[folder.uuid] = folder
            if folder.parent_uuid not in parent_dict:
                parent_dict[folder.parent_uuid] = []
            parent_dict[folder.parent_uuid].append(folder)
        self.context["folders_dict"] = folders_dict
        self.context["parent_dict"] = parent_dict
        return self

    def build_groups_dict(self):
        groups_dict = {g.uuid: g for g in self.context["available_groups"]}
        self.context["groups_dict"] = groups_dict
        return self

    def buid_users_dict(self):
        users_dict = {u.uuid: u for u in self.context["available_users"]}
        self.context["users_dict"] = users_dict
        return self

    def build(self) -> Context:
        return self.context


def build_folder_actions(context: Context, folder: Folder, has_access: bool):
    if has_access:
        return ["OPEN"]
    return []


def build_folder(context: Context, folder: Folder, has_access: bool):
    return {
        "name": folder.name,
        "uuid": folder.uuid,
        "stop_inherit": folder.stop_inherit,
        "has_access": has_access,
        "actions": build_folder_actions(context, folder, has_access),
    }


def build_children(context: Context, folder: Folder, user: RlcUser):
    if folder.uuid not in context["parent_dict"]:
        return []

    child_folders = context["parent_dict"][folder.uuid]

    children = []
    for child in child_folders:
        children.append(build_node(context, child, user))
    return children


def build_user_access(context: Context, folder: Folder, source="direct"):
    access = []
    for key in folder.keys:
        user = context["users_dict"].get(key.owner_uuid, None)
        if user is None:
            continue
        access.append(
            {
                "name": user.name,
                "uuid": key.owner_uuid,
                "is_valid": key.is_valid,
                "source": source,
                "actions": ["REVOKE_ACCESS"] if source == "direct" else [],
            }
        )
    if not folder.stop_inherit and folder.parent_uuid is not None:
        access += build_user_access(
            context, context["folders_dict"][folder.parent_uuid], "parent"
        )
    return access


def build_group_access(context: Context, folder: Folder, source="direct"):
    access = []
    for key in folder.group_keys:
        group = context["groups_dict"].get(key.owner_uuid, None)
        if group is None:
            continue
        access.append(
            {
                "name": group.name,
                "uuid": key.owner_uuid,
                "is_valid": key.is_valid,
                "source": source,
                "actions": ["REVOKE_ACCESS"] if source == "direct" else [],
            }
        )
    if not folder.stop_inherit and folder.parent_uuid is not None:
        access += build_group_access(
            context, context["folders_dict"][folder.parent_uuid], "parent"
        )
    return access


def build_node(context: Context, folder: Folder, user: RlcUser):
    has_access = folder.has_access(user)
    return {
        "folder": build_folder(context, folder, has_access),
        "children": build_children(context, folder, user),
        "content": folder.items if has_access else [],
        "access": build_user_access(context, folder),
        "group_access": build_group_access(context, folder),
    }


def build_tree(context: Context, user: RlcUser):
    nodes = []
    for folder in context["parent_dict"].get(None, []):
        node = build_node(context, folder, user)
        nodes.append(node)
    return nodes


def get_page(context: Context, user: RlcUser):
    return {
        "tree": build_tree(context, user),
        "available_persons": context["available_users"],
        "available_groups": context["available_groups"],
    }


@router.get(output_schema=OutputFolderPage)
def query__list_folders(rlc_user: RlcUser):
    builder = ContextBuilder()
    builder.build_available_users(rlc_user.org_id).buid_users_dict()
    builder.build_available_groups(rlc_user.org_id).build_groups_dict()
    builder.build_folders(rlc_user.org_id).build_folder_dicts()
    context = builder.build()
    return get_page(context, rlc_user)


@router.get(url="available_folders/", output_schema=list[schemas.OutputAvailableFolder])
def query__available_folders(rlc_user: RlcUser):
    r = get_repository()
    folders_1 = r.get_list(rlc_user.org_id)
    folders_2 = list(map(lambda f: {"id": f.uuid, "name": f.name}, folders_1))
    return folders_2


@router.get(
    url="<uuid:id>/",
    output_schema=schemas.OutputFolderDetail,
)
def query__detail_folder(rlc_user: RlcUser, data: schemas.InputFolderDetail):
    r = get_repository()
    builder = ContextBuilder()
    builder.build_available_users(rlc_user.org_id).buid_users_dict()
    builder.build_folders(rlc_user.org_id).build_folder_dicts()
    builder.build_available_groups(rlc_user.org_id).build_groups_dict()
    context = builder.build()
    folder = r.retrieve(rlc_user.org_id, data.id)

    for item in folder.items:
        if item.repository == "RECORD":
            item_repository = cast(
                ItemRepository, RepositoryWarehouse.get(item.repository)
            )
            record = cast(DataSheet, item_repository.retrieve(item.uuid, folder.org_pk))
            with transaction.atomic():
                for file in list(record.documents.all()):
                    if file.key is None and file.record:
                        file.key = file.record.key
                        file.save()
                    if file.folder_uuid is None:
                        file.folder_uuid = folder.uuid
                        folder.add_item(file)
                        file.save()
                r.save(folder)

    subfolders = r.get_children(rlc_user.org_id, folder.uuid)

    return {
        "folder": folder.as_dict(),
        "content": folder.items,
        "subfolders": subfolders,
        "access": build_user_access(context, folder),
        "group_access": build_group_access(context, folder),
    }
