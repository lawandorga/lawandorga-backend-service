from uuid import UUID

from pydantic import BaseModel


class InputAddDomain(BaseModel):
    domain: str


class InputCreateAlias(BaseModel):
    localpart: str
    domain: UUID


class InputDeleteAlias(BaseModel):
    id: UUID


class InputSetDefaultAlias(BaseModel):
    id: UUID
