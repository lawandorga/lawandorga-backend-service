from datetime import date
from typing import Any, List, Optional

from pydantic import BaseModel


class OutputIndividualUserActionsMonth(BaseModel):
    email: str
    actions: int


class OutputRawNumbers(BaseModel):
    records: int
    files: int
    collabs: int
    users: int
    lcs: int


class OutputRecordClientSex(BaseModel):
    value: str
    count: int


class OutputRecordClientState(BaseModel):
    value: str
    count: int


class OutputRecordClientAge(BaseModel):
    value: str
    count: int


class OutputRecordClientNationality(BaseModel):
    value: str
    count: int


class OutputTag(BaseModel):
    tag: str
    count: int


class OutputRecordStates(BaseModel):
    state: str
    amount: int


class OutputState(BaseModel):
    state: str
    count: int


class OutputRecordTagStats(BaseModel):
    tags: list[OutputTag]
    state: list[OutputState]
    years: list[int]


class OutputUsersWithMissingAccess(BaseModel):
    user: int
    records: int
    access: int


class OutputErrorsMonth(BaseModel):
    status: int
    path: str
    count: int


class OutputErrorsUser(BaseModel):
    email: str | int
    rlckeys: int
    userkeys: int
    accepted: bool
    locked: bool


class OutputUserActions(BaseModel):
    email: str | int
    actions: int


class OutputUniqueUsers(BaseModel):
    month: str
    logins: int


class OutputUserLogins(BaseModel):
    date: str | date
    logins: int


class OutputUserLoginsMonth(BaseModel):
    month: str
    logins: int


class OutputOrgUsage(BaseModel):
    lc: str
    records: int
    files: int
    documents: int


class OutputOrgMembers(BaseModel):
    name: str
    amount: int


class OutputMigrationStatistic(BaseModel):
    records: float
    records_togo: int
    documents: float
    documents_togo: int


class InputRecordStats(BaseModel):
    field_1: str
    value_1: str
    field_2: str


class OutputRecordStats(BaseModel):
    error: bool
    label: str
    data: List[tuple[Any, int, int]]


class OutputUserWithMissingRecordKeys(BaseModel):
    user: int
    records: int
    access: int


class OutputRecordClosedStatistic(BaseModel):
    days: Optional[int]
    count: int


class OutputRecordFieldAmount(BaseModel):
    field: str
    amount: int
