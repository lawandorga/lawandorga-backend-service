from typing import Literal
from uuid import UUID

from django.conf import settings
from django.db import models
from django.db.models import ProtectedError

from core.auth.models import OrgUser
from core.data_sheets.models import DataSheetTemplate
from core.data_sheets.models.template import (
    DataSheetEncryptedFileField,
    DataSheetEncryptedSelectField,
    DataSheetEncryptedStandardField,
    DataSheetMultipleField,
    DataSheetSelectField,
    DataSheetStandardField,
    DataSheetStateField,
    DataSheetUsersField,
)
from core.data_sheets.use_cases.finders import find_field_from_uuid, template_from_id
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def create_template(__actor: OrgUser, name: str):
    template = DataSheetTemplate.create(name=name, org=__actor.org)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def update_template(__actor: OrgUser, template_id: int, template_name: str):
    template = template_from_id(__actor, template_id)
    template.update_name(template_name)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def delete_template(__actor: OrgUser, template_id: int):
    template = template_from_id(__actor, template_id)
    if template.records.exists():
        raise UseCaseError(
            "This template can not be deleted as there are records that depend on it."
        )
    template.delete()


FIELDS: dict[str, type[models.Model]] = {
    "standard": DataSheetStandardField,
    "select": DataSheetSelectField,
    "multiple": DataSheetMultipleField,
    "state": DataSheetStateField,
    "users": DataSheetUsersField,
    "encryptedstandard": DataSheetEncryptedStandardField,
    "encryptedselect": DataSheetEncryptedSelectField,
    "encryptedfile": DataSheetEncryptedFileField,
}

FIELD_TYPES = Literal[
    "standard",
    "select",
    "multiple",
    "state",
    "users",
    "encryptedstandard",
    "encryptedselect",
    "encryptedfile",
]


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def create_field(
    __actor: OrgUser, template_id: int, kind: FIELD_TYPES, name: str, order: int
):
    template = template_from_id(__actor, template_id)
    field_model = FIELDS[kind]
    field = field_model(name=name, order=order, template=template)
    field.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def update_field(
    __actor: OrgUser,
    field_uuid: UUID,
    name: str,
    order: int,
    options: list[str] | None = None,
    share_keys: bool | None = None,
    group_id: int | None = None,
    field_type: str | None = None,
):
    field = find_field_from_uuid(__actor, field_uuid)
    field.name = name
    field.order = order
    kind = getattr(field, "kind", None)
    if kind in ["Multiple", "Select", "Encrypted Select"] and options is not None:
        setattr(field, "options", options)
    if kind in ["Users"] and share_keys is not None:
        setattr(field, "share_keys", share_keys)
    if group_id is not None:
        setattr(field, "group_id", group_id)
    if kind in ["Encrypted Standard", "Standard"] and field_type is not None:
        setattr(field, "field_type", field_type)
    field.save()


@use_case
def delete_field(__actor: OrgUser, field_uuid: UUID, force_delete: bool):
    field = find_field_from_uuid(__actor, field_uuid)

    if force_delete:
        field.get_entry_model().objects.filter(field=field).delete()

    try:
        field.delete()
    except ProtectedError:
        entries = (
            field.get_entry_model().objects.filter(field=field).select_related("record")
        )
        records = [e.record for e in entries]
        record_urls = [
            "{}/folders/{}/".format(settings.MAIN_FRONTEND_URL, record.folder_uuid)
            for record in records
        ]
        record_text = "\n".join(record_urls)
        raise UseCaseError(
            "This field has associated data from one or more records. "
            "Please empty this field in the following records:\n{}".format(record_text)
        )
