from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputPageGroup(BaseModel):
    group: UUID


class InputPageUser(BaseModel):
    user: UUID


class InputCheckDomain(BaseModel):
    domain: UUID


# query
class OutputDomain(BaseModel):
    uuid: UUID
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class OutputAddress(BaseModel):
    uuid: UUID
    localpart: str
    domain: OutputDomain
    is_default: bool

    model_config = ConfigDict(from_attributes=True)


class OutputUser(BaseModel):
    name: str
    uuid: UUID
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OutputPassword(BaseModel):
    password: str


class OutputSelfAccount(BaseModel):
    addresses: list[OutputAddress]

    model_config = ConfigDict(from_attributes=True)


class OutputSelfGroup(BaseModel):
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OutputSelfMailUser(BaseModel):
    uuid: UUID
    email: Optional[str]
    account: OutputSelfAccount
    aliases: list[str]
    groups: list[OutputSelfGroup]

    model_config = ConfigDict(from_attributes=True)


class OutputGroup(BaseModel):
    uuid: UUID
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OutputPageMail(BaseModel):
    user: OutputSelfMailUser
    available_domains: list[OutputDomain]
    domain: Optional[OutputDomain]
    users: list[OutputUser]
    groups: list[OutputGroup]


class OutputPageGroup(BaseModel):
    available_domains: list[OutputDomain]
    available_users: list[OutputUser]
    addresses: list[OutputAddress]
    members: list[OutputUser]


class OutputPageUser(BaseModel):
    available_domains: list[OutputDomain]
    addresses: list[OutputAddress]


class OutputDomainCheck(BaseModel):
    valid: bool
    wrong_setting: None | str
