from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import UploadedFile

from core.auth.models import OrgUser
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import UseCaseError, use_case
from core.upload.models import UploadLink
from core.upload.use_cases.finder import link_from_uuid, link_from_uuid_dangerous


@use_case
def create_upload_link(__actor: OrgUser, name: str, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)
    link = UploadLink.create(name, folder, __actor)
    link.save()


@use_case
def disable_upload_link(__actor: OrgUser, link_uuid: UUID):
    link = link_from_uuid(__actor, link_uuid)
    link.disable()
    link.save()


@use_case
def delete_upload_link(__actor: OrgUser, link_uuid: UUID):
    link = link_from_uuid(__actor, link_uuid)
    if link.files.count() > 0:
        raise UseCaseError("This link can not be deleted as files have been uploaded.")

    link.delete()


@use_case
def upload_data(__actor: AnonymousUser, name: str, file: UploadedFile, link_uuid: UUID):
    link = link_from_uuid_dangerous(link_uuid)
    obj = link.upload(name, file)
    obj.save()
