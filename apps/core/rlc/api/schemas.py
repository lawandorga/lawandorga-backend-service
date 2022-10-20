from uuid import UUID

from pydantic import AnyUrl, BaseModel


class InputExternalLinkDelete(BaseModel):
    id: UUID


class InputExternalLinkCreate(BaseModel):
    name: str
    link: AnyUrl
    order: int


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
