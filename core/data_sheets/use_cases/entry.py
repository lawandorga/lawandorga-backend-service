from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models.org_user import OrgUser
from core.data_sheets.models.data_sheet import DataSheet
from core.data_sheets.use_cases.finders import (
    find_field_from_uuid,
    find_file_field_from_uuid,
    find_record_from_folder_uuid,
    find_sheets_from_folder_uuid,
    sheet_from_id,
)
from core.seedwork.use_case_layer import use_case


def update_record_in_folder(__actor: OrgUser, folder_uuid: UUID):
    record = find_record_from_folder_uuid(__actor, folder_uuid)
    if not record:
        return
    sheets = find_sheets_from_folder_uuid(__actor, folder_uuid)
    record.set_attributes(sheets)
    record.save()


def set_sheet_updated_time(sheet: DataSheet):
    sheet.save()


@use_case
def create_file_entry(
    __actor: OrgUser, field_id: UUID, record_id: int, file: UploadedFile
):
    field = find_file_field_from_uuid(__actor, field_id)
    field.delete_old_entries(record_id)
    field.upload_file(__actor, record_id, file)
    sheet = sheet_from_id(__actor, record_id)
    set_sheet_updated_time(sheet)


@use_case
def create_entry(
    __actor: OrgUser, field_id: UUID, record_id: int, value: str | list[str]
):
    field = find_field_from_uuid(__actor, field_id)
    field.create_entry(__actor, record_id, value)
    sheet = sheet_from_id(__actor, record_id)
    set_sheet_updated_time(sheet)
    update_record_in_folder(__actor, sheet.folder_uuid)


@use_case
def update_entry(
    __actor: OrgUser, field_id: UUID, record_id: int, value: str | list[str]
):
    field = find_field_from_uuid(__actor, field_id)
    field.update_entry(__actor, record_id, value)
    sheet = sheet_from_id(__actor, record_id)
    set_sheet_updated_time(sheet)
    update_record_in_folder(__actor, sheet.folder_uuid)


@use_case
def create_or_update_entry(
    __actor: OrgUser, field_id: UUID, record_id: int, value: str | list[str]
):
    field = find_field_from_uuid(__actor, field_id)
    field.create_or_update_entry(__actor, record_id, value)
    sheet = sheet_from_id(__actor, record_id)
    set_sheet_updated_time(sheet)
    update_record_in_folder(__actor, sheet.folder_uuid)


@use_case
def delete_entry(__actor: OrgUser, field_id: UUID, record_id: int):
    field = find_field_from_uuid(__actor, field_id)
    field.delete_entry(record_id)
    sheet = sheet_from_id(__actor, record_id)
    set_sheet_updated_time(sheet)
    update_record_in_folder(__actor, sheet.folder_uuid)
