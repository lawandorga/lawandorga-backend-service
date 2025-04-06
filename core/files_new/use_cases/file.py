from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models import OrgUser
from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.finder import file_from_uuid
from core.folders.usecases.finders import folder_from_uuid
from core.seedwork.use_case_layer import UseCaseError, use_case
from messagebus.domain.collector import EventCollector


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
