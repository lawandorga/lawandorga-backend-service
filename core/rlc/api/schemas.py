from uuid import UUID

from pydantic import AnyUrl, BaseModel

from core.seedwork.api_layer import qs_to_list


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
    description: str

    class Config:
        orm_mode = True


class OutputPermission(BaseModel):
    id: int
    permission_name: str

    class Config:
        orm_mode = True


class OutputMember(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


class OutputSingleGroup(BaseModel):
    id: int
    name: str
    description: str
    permissions: list[OutputPermission]
    members: list[OutputMember]

    _ = qs_to_list("members")
    __ = qs_to_list("permissions")

    class Config:
        orm_mode = True


class OutputExternalLink(BaseModel):
    id: UUID
    name: str
    link: AnyUrl
    order: int

    class Config:
        orm_mode = True


class InputListUsersGet(BaseModel):
    id: int


class OutputGroupMember(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        orm_mode = True


class InputAddMember(BaseModel):
    id: int
    new_member: int


class InputRemoveMember(BaseModel):
    id: int
    member: int
