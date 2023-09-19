from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict


class InputNoteCreate(BaseModel):
    title: str
    note: str


class InputNoteUpdate(BaseModel):
    title: str
    note: str
    id: int


class InputNoteDelete(BaseModel):
    id: int


class OutputNote(BaseModel):
    id: int
    title: str
    note: str

    model_config = ConfigDict(from_attributes=True)


class InputAcceptMember(BaseModel):
    user: int


class InputExternalLinkDelete(BaseModel):
    id: UUID


class InputGroupCreate(BaseModel):
    name: str
    description: str | None = None


class InputGroupUpdate(BaseModel):
    name: str
    description: str | None = None
    id: int


class InputGroupDelete(BaseModel):
    id: int


class InputExternalLinkCreate(BaseModel):
    name: str
    link: AnyUrl
    order: int


class InputQueryGroup(BaseModel):
    id: int


class OutputGroup(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class OutputPermission(BaseModel):
    id: int
    permission_name: str

    model_config = ConfigDict(from_attributes=True)


class OutputMember(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class OutputSingleGroup(BaseModel):
    id: int
    name: str
    description: str | None
    permissions: list[OutputPermission]
    members: list[OutputMember]

    model_config = ConfigDict(from_attributes=True)


class OutputExternalLink(BaseModel):
    id: UUID
    name: str
    link: str
    order: int

    model_config = ConfigDict(from_attributes=True)


class InputListUsersGet(BaseModel):
    id: int


class OutputGroupMember(BaseModel):
    id: int
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class InputAddMember(BaseModel):
    id: int
    new_member: int


class InputRemoveMember(BaseModel):
    id: int
    member: int
