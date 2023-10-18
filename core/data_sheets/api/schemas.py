from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputFieldDelete(BaseModel):
    uuid: UUID
    force_delete: bool = False


class InputTemplateDetail(BaseModel):
    id: int


class InputQueryRecord(BaseModel):
    uuid: UUID


class InputRecordCreate(BaseModel):
    name: str
    template: int


class InputRecordCreateWithinFolder(BaseModel):
    name: str
    template: int
    folder: UUID


class InputAccess(BaseModel):
    id: int


class InputDeleteDataSheet(BaseModel):
    uuid: UUID


class InputCreateAccess(BaseModel):
    record: int
    explanation: str = ""


class InputRecordChangeName(BaseModel):
    id: int
    name: str


class InputDeletion(BaseModel):
    id: int


class InputCreateDeletion(BaseModel):
    record: int
    explanation: str = ""


class InputTemplateCreate(BaseModel):
    name: str


class InputTemplateDelete(BaseModel):
    id: int


class InputTemplateUpdate(BaseModel):
    id: int
    name: str
    show: list[str]


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

    model_config = ConfigDict(from_attributes=True)


class OutputTemplateDetail(OutputTemplate):
    fields: list[OutputTemplateField]


class OutputRecordDeletion(BaseModel):
    created: datetime
    explanation: str
    id: int
    processed_by_detail: str
    record_detail: str
    requested_by_detail: str
    state: str
    processed: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class OutputRecordAccess(BaseModel):
    created: datetime
    id: int
    processed_by_detail: str
    requested_by_detail: str
    record_detail: str
    state: str
    processed_on: Optional[datetime]
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class OutputRecordCreate(BaseModel):
    id: int
    folder_uuid: UUID
    uuid: UUID


class OutputEntry(BaseModel):
    value: str

    model_config = ConfigDict(from_attributes=True)


class OutputField(BaseModel):
    id: int
    entry_url: str
    kind: str
    label: str
    name: str
    options: Optional[list[OutputOption | str]] = None
    type: str


class OutputDetailEntry(BaseModel):
    name: str
    type: str
    url: str
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


class OutputRecord(BaseModel):
    id: int
    uuid: UUID
    attributes: dict[str, Union[str, list[str]]]
    delete_requested: bool
    has_access: bool
    folder_uuid: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


class OutputRecordsPage(BaseModel):
    columns: list[str]
    records: list[OutputRecord]
