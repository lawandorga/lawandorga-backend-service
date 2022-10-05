from uuid import UUID

from pydantic import AnyUrl, BaseModel


class ExternalLinkDelete(BaseModel):
    id: UUID


class ExternalLinkCreate(BaseModel):
    name: str
    link: AnyUrl
    order: int


class ExternalLink(BaseModel):
    id: UUID
    name: str
    link: AnyUrl
    order: int

    class Config:
        orm_mode = True


class ListUsersGetInput(BaseModel):
    id: int


class GroupMember(BaseModel):
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
