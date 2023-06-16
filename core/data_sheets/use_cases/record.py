from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.data_sheets.models import Record, RecordTemplate
from core.data_sheets.use_cases.finders import (
    record_from_id,
    record_from_uuid,
    template_from_id,
)
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.folders.use_cases.finders import folder_from_uuid
from core.permissions.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def change_record_name(__actor: RlcUser, name: str, record_id: int):
    record = record_from_id(__actor, record_id)
    record.set_name(name)
    record.save()


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_record_and_a_folder(
    __actor: RlcUser,
    name: str,
    template_id: int,
) -> UUID:
    template = template_from_id(__actor, template_id)

    folder_repository = cast(
        FolderRepository, RepositoryWarehouse.get(FolderRepository)
    )
    parent_folder = folder_repository.get_or_create_records_folder(
        __actor.org_id, __actor
    )

    if not parent_folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    folder = Folder.create(name=name, org_pk=__actor.org_id, stop_inherit=True)
    folder.grant_access(__actor)
    folder.set_parent(parent_folder, __actor)
    folder_repository.save(folder)

    return __create(__actor, name, folder, template)


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_data_sheet_within_a_folder(
    __actor: RlcUser,
    name: str,
    folder_uuid: UUID,
    template_id: int,
) -> UUID:
    folder = folder_from_uuid(__actor, folder_uuid)
    template = template_from_id(__actor, template_id)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    return __create(__actor, name, folder, template)


def __create(
    __actor: RlcUser, name: str, folder: Folder, template: RecordTemplate
) -> UUID:
    access_granted = False
    for user in list(__actor.org.users.all()):
        should_access = user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)
        has_access = folder.has_access(user)
        if should_access and not has_access:
            folder.grant_access(user, __actor)
            access_granted = True

    if access_granted:
        folder_repository = cast(
            FolderRepository, RepositoryWarehouse.get(FolderRepository)
        )
        folder_repository.save(folder)

    record = Record(template=template, name=name)
    record.set_folder(folder)
    record.generate_key(__actor)
    record.save()

    return record.uuid


@use_case
def migrate_record_into_folder(__actor: RlcUser, record: Record):
    user = __actor

    if not record.has_access(user):
        raise ValueError("User has no access to this folder.")

    if record.folder_uuid is not None:
        raise ValueError("This record is already inside a folder.")

    # put the record inside a folder
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))

    records_folder = r.get_or_create_records_folder(
        org_pk=record.template.rlc_id, user=user
    )

    folder_name = "{}".format(record.identifier or "Not-Set")
    folder = Folder.create(
        folder_name, org_pk=record.template.rlc_id, stop_inherit=True
    )
    folder.grant_access(user)
    folder.set_parent(records_folder, user)

    for encryption in list(record.encryptions.exclude(user_id=user.id)):
        folder.grant_access(to=encryption.user, by=user)

    record.set_folder(folder)

    # get the key of the record
    private_key_user = user.get_decryption_key().get_private_key()
    encryption = record.encryptions.get(user=user)
    encryption.decrypt(private_key_user)
    aes_key: str = encryption.key  # type: ignore
    aes_key_box = OpenBox(data=bytes(aes_key, "utf-8"))
    key = SymmetricKey(key=aes_key_box, origin=SymmetricEncryptionV1.VERSION)
    encryption_key = folder.get_encryption_key(requestor=user)
    record.key = EncryptedSymmetricKey.create(key, encryption_key).as_dict()

    # save the record and the folder
    r.save(folder)
    record.save()


@use_case(permissions=[PERMISSION_RECORDS_ACCESS_ALL_RECORDS])
def delete_data_sheet(__actor: RlcUser, sheet_uuid: UUID):
    record = record_from_uuid(__actor, sheet_uuid)
    record.delete()
