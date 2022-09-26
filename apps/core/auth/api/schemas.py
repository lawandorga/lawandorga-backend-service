from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Rlc(BaseModel):
    id: int
    name: str
    use_record_pool: bool

    class Config:
        orm_mode = True


class InputRlcUserUpdate(BaseModel):
    id: int
    name: Optional[str]
    birthday: Optional[Any]
    phone_number: Optional[str]
    street: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    speciality_of_study: Optional[str]
    note: Optional[str]


class InputRlcUserGet(BaseModel):
    id: int


class RlcUser(BaseModel):
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

    class Config:
        orm_mode = True


class Badges(BaseModel):
    profiles: int
    record_deletion_requests: int
    record_permit_requests: int
    legal: int


class RlcUserData(BaseModel):
    user: RlcUser
    rlc: Rlc
    badges: Badges
    permissions: List[str]
    settings: Optional[Dict]
