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
