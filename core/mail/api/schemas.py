from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InputAddDomain(BaseModel):
    domain: str


class InputCreateAlias(BaseModel):
    localpart: str
    domain: UUID
    user: UUID


class InputDeleteAlias(BaseModel):
    alias: UUID


class InputSetDefaultAlias(BaseModel):
    alias: UUID


class OutputMailUser(BaseModel):
    id: Optional[UUID]
    email: Optional[str]

    class Config:
        orm_mode = True
