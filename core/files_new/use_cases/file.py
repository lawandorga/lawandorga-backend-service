from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models import OrgUser
from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.finder import file_from_uuid
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def upload_a_file(__actor: OrgUser, file: UploadedFile, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not upload a file into this folder, because you have no access to this folder."
        )

    f = EncryptedRecordDocument.create(file, folder, __actor)
    f.upload(file, __actor)
    f.save()


@use_case
def delete_a_file(__actor: OrgUser, file_uuid: UUID):
    file = file_from_uuid(__actor, file_uuid)
    file.delete_on_cloud()
    file.delete()


@use_case
def put_files_inside_of_folders(__actor: OrgUser):
    files1 = (
        EncryptedRecordDocument.objects.filter(folder_uuid=None)
        .filter(org=__actor.org)
        .exclude(record=None)
        .select_related("record")
    )
    files2: list[EncryptedRecordDocument] = list(files1)
    for file in files2:
        if file.record:
            record = file.record
            if record.folder_uuid:
                folder = record.folder.folder

                file.key = file.record.key
                file.folder.put_obj_in_folder(folder)
                file.save()
