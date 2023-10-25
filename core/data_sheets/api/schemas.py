from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputTemplateDetail(BaseModel):
    id: int


class InputQueryRecord(BaseModel):
    uuid: UUID


class InputRecordCreateWithinFolder(BaseModel):
    name: str
    template: int
    folder: UUID


class OutputOption(BaseModel):
    name: str
    id: int


class OutputAccessPerson(BaseModel):
    name: str
    uuid: UUID


class OutputNonMigratedDataSheet(BaseModel):
    attributes: dict[str, Union[str, list[str]]]
    name: str
    token: str
    uuid: UUID
    persons_with_access: list[OutputAccessPerson]

    model_config = ConfigDict(from_attributes=True)


class OutputTemplate(BaseModel):
    name: str
    id: int

    model_config = ConfigDict(from_attributes=True)


class OutputTemplateField(BaseModel):
    encrypted: str
    type: str
    name: str
    uuid: UUID
    field_type: str
    order: int
    kind: str
    group_id: int | None = None
    share_keys: bool | None = None
    options: Optional[list[OutputOption | str]] = None

    model_config = ConfigDict(from_attributes=True)


class OutputTemplateDetail(OutputTemplate):
    fields: list[OutputTemplateField]


class OutputRecordCreate(BaseModel):
    id: int
    folder_uuid: UUID
    uuid: UUID


class OutputField(BaseModel):
    id: int
    uuid: UUID
    kind: str
    label: str
    name: str
    options: Optional[list[OutputOption | str]] = None
    type: str


class OutputDetailEntry(BaseModel):
    id: int
    name: str
    type: str
    value: str | int | list[int] | list[str]


class OutputClient(BaseModel):
    name: str
    phone_number: str
    note: str

    model_config = ConfigDict(from_attributes=True)


class OutputRecordDetail(BaseModel):
    created: datetime
    updated: datetime
    id: int
    uuid: UUID
    folder_uuid: UUID
    name: str
    client: Optional[OutputClient]
    fields: list[OutputField]
    entries: dict[str, OutputDetailEntry]
    template_name: str
