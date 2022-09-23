from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RlcUser(BaseModel):
    name: str
    id: int

    class Config:
        orm_mode = True


class LegalRequirement(BaseModel):
    title: str
    content: str

    class Config:
        orm_mode = True


class LegalRequirementEvent(BaseModel):
    actor: Optional[RlcUser]
    text: str
    accepted: bool
    created: datetime

    class Config:
        orm_mode = True


class LegalRequirementUser(BaseModel):
    legal_requirement: LegalRequirement
    rlc_user_id: int
    accepted: bool
    events_list: List[LegalRequirementEvent]

    class Config:
        orm_mode = True


class LegalRequirementEventCreate(BaseModel):
    id: int
    actor: int
    accepted: bool
