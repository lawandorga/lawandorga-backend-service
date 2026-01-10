from uuid import UUID

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import Q

from core.auth.models import OrgUser
from core.files.models import Folder, PermissionForFolder
from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.finder import file_from_uuid
from core.folders.domain.aggregates.folder import Folder as DFolder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.models import FOL_Folder
from core.folders.use_cases.finders import folder_from_uuid
from core.org.models.group import Group
from core.permissions.models import HasPermission, Permission
from core.permissions.static import (
    PERMISSION_FILES_READ_ALL_FOLDERS,
    PERMISSION_FILES_WRITE_ALL_FOLDERS,
)
from core.seedwork.use_case_layer import UseCaseError, use_case
from messagebus.domain.collector import EventCollector

from seedwork.functional import list_filter, list_map


@use_case
def upload_a_file(
    __actor: OrgUser, file: UploadedFile, folder_uuid: UUID, collector: EventCollector
) -> EncryptedRecordDocument:
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not upload a file into this folder, because you have no access to this folder."
        )

    f = EncryptedRecordDocument.create(file, folder, __actor, collector)
    f.upload(file, __actor)
    f.save()
    return f


@use_case
def upload_multiple_files(
    __actor: OrgUser,
    files: list[UploadedFile],
    folder_uuid: UUID,
    collector: EventCollector,
):
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not upload a file into this folder, because you have no access to this folder."
        )

    for file in files:
        f = EncryptedRecordDocument.create(file, folder, __actor, collector)
        f.upload(file, __actor)
        f.save()


@use_case
def delete_file(__actor: OrgUser, file_uuid: UUID, collector: EventCollector):
    file = file_from_uuid(__actor, file_uuid)
    file.delete_on_cloud()
    file.delete(collector)


def get_users_and_groups(actor: OrgUser):
    read_permission = Permission.objects.get(name=PERMISSION_FILES_READ_ALL_FOLDERS)
    write_permission = Permission.objects.get(name=PERMISSION_FILES_WRITE_ALL_FOLDERS)
    permissions = HasPermission.objects.filter(
        Q(user__org=actor.org) | Q(group_has_permission__org=actor.org),
        permission__in=[read_permission, write_permission],
    )
    groups = set()
    for perm in permissions:
        if perm.group_has_permission:
            groups.add(perm.group_has_permission)
    users = set()
    for perm in permissions:
        if perm.user:
            users.add(perm.user)
    return users, groups


def build_new_tree(
    actor: OrgUser,
    current_folder: Folder,
    parent: DFolder,
    global_users: set[OrgUser],
    global_groups: set[Group],
) -> list[DFolder]:
    new_folders = []
    childs = current_folder.child_folders.all().prefetch_related("child_folders")
    for folder in childs:
        f_permissions = PermissionForFolder.objects.filter(
            folder=folder
        ).select_related("group_has_permission")
        groups_with_access = list_map(f_permissions, lambda p: p.group_has_permission)
        dfolder = DFolder.create(
            name=folder.name, org_pk=actor.org_id, stop_inherit=False
        )
        for group in groups_with_access:
            dfolder.grant_access_to_group(group, actor)
        for u in global_users:
            if not dfolder.has_access(u):
                dfolder.grant_access(u, actor)
        for group in global_groups:
            if not dfolder.has_keys(group):
                dfolder.grant_access_to_group(group, actor)
        dfolder.set_parent(parent, actor)
        new_folders.append(dfolder)
        child_new_folders = build_new_tree(
            actor, folder, dfolder, global_users, global_groups
        )
        new_folders.extend(child_new_folders)
    return new_folders


@use_case(permissions=[PERMISSION_FILES_WRITE_ALL_FOLDERS])
def migrate_old_files(__actor: OrgUser):
    # delete
    FOL_Folder.objects.filter(
        org=__actor.org, name="Migrated Files (Feel free to rename)"
    ).delete()
    # migrate
    all_folders = Folder.objects.filter(rlc=__actor.org).select_related("parent")
    parent_folders = list_filter(all_folders, lambda f: f.parent is None)
    new_parent_folder = DFolder.create(
        name="Migrated Files (Feel free to rename)",
        org_pk=__actor.org_id,
        stop_inherit=False,
    )
    new_parent_folder.grant_access(__actor)
    global_users, global_groups = get_users_and_groups(__actor)
    for g in global_groups:
        new_parent_folder.grant_access_to_group(g, __actor)
    for u in global_users:
        if not new_parent_folder.has_access(u):
            new_parent_folder.grant_access(u, __actor)
    new_folders = [new_parent_folder]
    for folder in parent_folders:
        new_folders.extend(
            build_new_tree(
                __actor, folder, new_parent_folder, global_users, global_groups
            )
        )
    r = DjangoFolderRepository()
    with transaction.atomic():
        for f in new_folders:
            r.save(f)
