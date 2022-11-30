from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


# page
class InputPageGroup(BaseModel):
    group: UUID


class InputPageUser(BaseModel):
    user: UUID


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


class OutputAddress(BaseModel):
    uuid: UUID
    localpart: str
    domain: OutputDomain
    is_default: bool

    class Config:
        orm_mode = True


class OutputUser(BaseModel):
    name: str
    uuid: UUID
    email: Optional[str]

    class Config:
        orm_mode = True


class OutputPassword(BaseModel):
    password: str


class OutputSelfAccount(BaseModel):
    addresses: list[OutputAddress]

    _ = qs_to_list("addresses")

    class Config:
        orm_mode = True


class OutputSelfGroup(BaseModel):
    email: Optional[str]

    class Config:
        orm_mode = True


class OutputSelfMailUser(BaseModel):
    uuid: UUID
    email: Optional[str]
    account: OutputSelfAccount
    aliases: list[str]
    groups: list[OutputSelfGroup]

    class Config:
        orm_mode = True

    _ = qs_to_list("groups")


class OutputGroup(BaseModel):
    uuid: UUID
    email: Optional[str]

    class Config:
        orm_mode = True


class OutputPageMail(BaseModel):
    user: OutputSelfMailUser
    available_domains: list[OutputDomain]
    domain: Optional[OutputDomain]
    users: list[OutputUser]
    groups: list[OutputGroup]

    __ = qs_to_list("users")
    _ = qs_to_list("groups")


class OutputPageGroup(BaseModel):
    available_domains: list[OutputDomain]
    available_users: list[OutputUser]
    addresses: list[OutputAddress]
    members: list[OutputUser]

    _ = qs_to_list("available_domains")
    __ = qs_to_list("addresses")
    ___ = qs_to_list("members")
    ____ = qs_to_list('available_users')


class OutputPageUser(BaseModel):
    available_domains: list[OutputDomain]
    addresses: list[OutputAddress]

    _ = qs_to_list("available_domains")
    __ = qs_to_list("addresses")
