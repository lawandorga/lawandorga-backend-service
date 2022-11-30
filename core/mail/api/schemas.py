from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


# group
class InputCreateGroupMail(BaseModel):
    localpart: str
    domain: UUID


class InputDeleteGroupMail(BaseModel):
    group: UUID


class InputAddMemberToGroupMail(BaseModel):
    group: UUID
    member: UUID


class InputRemoveMemberFromGroupMail(BaseModel):
    group: UUID
    member: UUID


class InputAddAddressToGroup(BaseModel):
    localpart: str
    group: UUID
    domain: UUID


class InputSetDefaultGroupAddress(BaseModel):
    group: UUID
    address: UUID


class InputDeleteGroupAddress(BaseModel):
    group: UUID
    address: UUID


# domain
class InputAddDomain(BaseModel):
    name: str


class InputChangeDomain(BaseModel):
    uuid: UUID
    name: str


# mail user
class InputCreateAddress(BaseModel):
    localpart: str
    domain: UUID
    user: UUID


class InputDeleteAddress(BaseModel):
    address: UUID


class InputSetDefaultAddress(BaseModel):
    address: UUID


# query
class OutputDomain(BaseModel):
    uuid: UUID
    name: str

    class Config:
        orm_mode = True


class OutputDomain2(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OutputAddress(BaseModel):
    uuid: UUID
    localpart: str
    domain: OutputDomain
    is_default: bool

    class Config:
        orm_mode = True


class OutputMailUser2(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OutputAccount2(BaseModel):
    user: Optional[OutputMailUser2]

    class Config:
        orm_mode = True


class OutputAddress2(BaseModel):
    localpart: str
    domain: OutputDomain2
    is_default: bool
    account: OutputAccount2

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
    uuid: UUID
    email: Optional[str]
    account: OutputAccount
    aliases: list[str]

    class Config:
        orm_mode = True


class OutputPageMail(BaseModel):
    user: OutputMailUser
    available_domains: list[OutputDomain]
    domain: Optional[OutputDomain]
    addresses: list[OutputAddress2]

    _ = qs_to_list("addresses")


class OutputNoAccount(BaseModel):
    no_mail_account = True
