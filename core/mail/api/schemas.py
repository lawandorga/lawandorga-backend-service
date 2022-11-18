from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


class InputAddDomain(BaseModel):
    domain: str


class InputCreateAddress(BaseModel):
    localpart: str
    domain: UUID
    user: UUID


class InputDeleteAddress(BaseModel):
    address: UUID


class InputSetDefaultAddress(BaseModel):
    address: UUID


class OutputDomain(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class OutputAddress(BaseModel):
    id: UUID
    localpart: str
    domain: OutputDomain
    is_default: bool

    class Config:
        orm_mode = True


class OutputPassword(BaseModel):
    password: str


class OutputAccount(BaseModel):
    addresses: list[OutputAddress]

    _ = qs_to_list("addresses")

    class Config:
        orm_mode = True


class OutputMailUser(BaseModel):
    id: UUID
    email: Optional[str]
    account: OutputAccount
    aliases: list[str]

    class Config:
        orm_mode = True


class OutputPageMail(BaseModel):
    user: OutputMailUser
    available_domains: list[OutputDomain]

    _ = qs_to_list("available_domains")


class OutputNoAccount(BaseModel):
    no_mail_account = True
