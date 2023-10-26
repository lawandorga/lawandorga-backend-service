from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models.org_user import RlcUser
from core.data_sheets.models.data_sheet import DataSheet
from core.data_sheets.use_cases.finders import (
    find_field_from_uuid,
    find_file_field_from_uuid,
)
from core.seedwork.use_case_layer import use_case


def update_record_updated_time(record_id: int):
    DataSheet.objects.get(pk=record_id).save()


@use_case
def create_entry(
    __actor: RlcUser, field_id: UUID, record_id: int, value: str | list[str]
):
    field = find_field_from_uuid(__actor, field_id)
    field.create_entry(__actor, record_id, value)
    update_record_updated_time(record_id)


@use_case
def create_file_entry(
    __actor: RlcUser, field_id: UUID, record_id: int, file: UploadedFile
):
    field = find_file_field_from_uuid(__actor, field_id)
    field.delete_old_entries(record_id)
    field.upload_file(__actor, record_id, file)
    update_record_updated_time(record_id)


@use_case
def update_entry(
    __actor: RlcUser, field_id: UUID, record_id: int, value: str | list[str]
):
    field = find_field_from_uuid(__actor, field_id)
    field.update_entry(__actor, record_id, value)
    update_record_updated_time(record_id)


@use_case
def delete_entry(__actor: RlcUser, field_id: UUID, record_id: int):
    field = find_field_from_uuid(__actor, field_id)
    field.delete_entry(record_id)
    update_record_updated_time(record_id)
