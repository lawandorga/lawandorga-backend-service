from typing import cast

from django.db import transaction

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_uuid
from core.records.models import Record, RecordTemplate
from core.records.use_cases.finders import record_from_id, template_from_id
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, find, use_case
from core.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)


@use_case
def change_record_name(__actor: RlcUser, name: str, record=find(record_from_id)):
    record.set_name(name)
    record.save()


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_record_and_a_folder(
    __actor: RlcUser,
    name: str,
    parent_folder=find(folder_from_uuid),
    template=find(template_from_id),
):
    if not parent_folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    folder = Folder.create(name=name, org_pk=__actor.org_id, stop_inherit=True)
    folder.grant_access(__actor)
    folder.set_parent(parent_folder, __actor)

    return __create(__actor, folder, template)


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_record_within_a_folder(
    __actor: RlcUser,
    folder=find(folder_from_uuid),
    template=find(template_from_id),
):
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    return __create(__actor, folder, template)


def __create(__actor: RlcUser, folder: Folder, template: RecordTemplate) -> int:
    for user in list(__actor.org.users.all()):
        if user.has_permission(
            PERMISSION_RECORDS_ACCESS_ALL_RECORDS
        ) and not folder.has_access(user):
            folder.grant_access(user, __actor)

    record = Record(template=template, name=folder.name)

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))

    folder.add_item(record)

    with transaction.atomic():
        r.save(folder)
        record.generate_key(__actor)
        record.save()

    return record.id
