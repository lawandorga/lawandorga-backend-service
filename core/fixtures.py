from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from core.models import CollabPermission, FolderPermission, Permission

from core.permissions.static import (
    get_all_collab_permission_strings,
    get_all_files_permission_strings,
    get_all_permission_strings,
)


def create_collab_permissions(collab_permission_model: "Type[CollabPermission]"):
    permissions = get_all_collab_permission_strings()
    for permission in permissions:
        collab_permission_model.objects.get_or_create(name=permission)


def create_permissions(permission_model: "Type[Permission]"):
    permissions = get_all_permission_strings()
    for permission in permissions:
        permission_model.objects.get_or_create(name=permission)


def create_folder_permissions(folder_permission_model: "Type[FolderPermission]"):
    permissions = get_all_files_permission_strings()
    for permission in permissions:
        folder_permission_model.objects.get_or_create(name=permission)


def create():
    from core.models import CollabPermission, FolderPermission, Permission

    create_permissions(Permission)
    create_collab_permissions(CollabPermission)
    create_folder_permissions(FolderPermission)
