from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OutputOrg(BaseModel):
    name: str
    id: int

    model_config = ConfigDict(from_attributes=True)


class OutputDashboardRecord(BaseModel):
    id: int
    uuid: UUID
    identifier: str
    state: str


class OutputDashboardMember(BaseModel):
    name: str
    id: int
    rlcuserid: int


class OutputDashboardQuestionnaire(BaseModel):
    name: str
    folder_uuid: UUID


class OutputDashboardChangedRecord(BaseModel):
    id: int
    uuid: UUID
    identifier: str
    updated: datetime


class OutputFollowUp(BaseModel):
    time: datetime
    title: str
    folder_uuid: UUID


class OutputDashboardPage(BaseModel):
    records: None | list[OutputDashboardRecord] = None
    members: None | list[OutputDashboardMember] = None
    questionnaires: None | list[OutputDashboardQuestionnaire] = None
    changed_records: None | list[OutputDashboardChangedRecord] = None
    follow_ups: None | list[OutputFollowUp] = None

    model_config = ConfigDict(from_attributes=True)


class OutputLegalRequirement(BaseModel):
    title: str
    id: int
    content: str
    accept_required: bool

    model_config = ConfigDict(from_attributes=True)


class OutputMatrixUser(BaseModel):
    _group: str
    matrix_id: str

    model_config = ConfigDict(from_attributes=True)


class OutputChatPage(BaseModel):
    matrix_user: OutputMatrixUser | None


class OutputRegisterPage(BaseModel):
    orgs: list[OutputOrg]
    legal_requirements: list[OutputLegalRequirement]

    model_config = ConfigDict(from_attributes=True)


class InputConfirmEmail(BaseModel):
    id: int
    token: str


class Link(BaseModel):
    id: UUID
    name: str
    link: str
    order: int

    model_config = ConfigDict(from_attributes=True)


class Rlc(BaseModel):
    id: int
    name: str
    links: List[Link]

    model_config = ConfigDict(from_attributes=True)


class InputRlcUserUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    birthday: Optional[Any] = None
    phone_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    speciality_of_study: Optional[str] = None
    note: Optional[str] = None


class InputRlcUserGrantPermission(BaseModel):
    id: int
    permission: int


class InputRlcUserGet(BaseModel):
    id: int


class InputRlcUserActivate(BaseModel):
    id: int


class OutputRlcUserOptional(BaseModel):
    id: int
    user_id: int
    birthday: Optional[Any] = None
    phone_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    locked: Optional[bool] = None
    locked_legal: Optional[bool] = None
    email_confirmed: Optional[bool] = None
    is_active: Optional[bool] = None
    accepted: Optional[bool] = None
    updated: Optional[datetime] = None
    note: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created: Optional[datetime] = None
    speciality_of_study: Optional[str] = None
    speciality_of_study_display: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OutputRlcUserSmall(BaseModel):
    id: int
    user_id: int
    phone_number: Optional[str]
    name: str
    email: str
    accepted: bool
    email_confirmed: bool
    locked: bool
    is_active: bool
    last_login_month: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OutputRlcUser(BaseModel):
    id: int
    user_id: int
    birthday: Optional[Any]
    phone_number: Optional[str]
    street: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    locked: bool
    locked_legal: bool
    email_confirmed: bool
    is_active: bool
    accepted: bool
    updated: datetime
    note: Optional[str]
    name: str
    email: str
    created: datetime
    speciality_of_study: Optional[str]
    speciality_of_study_display: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class Badges(BaseModel):
    profiles: int
    record_deletion_requests: int
    record_permit_requests: int
    legal: int
    record: int


class OutputRlcUserData(BaseModel):
    user: OutputRlcUser
    rlc: Rlc
    badges: Badges
    permissions: List[str]
    settings: Optional[Dict]


class OutputStatisticsUser(BaseModel):
    id: int
    user_id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class OutputStatisticsUserData(BaseModel):
    user: OutputStatisticsUser
