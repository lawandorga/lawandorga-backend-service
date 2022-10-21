from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class OutputRlcUser(BaseModel):
    name: str
    id: int

    class Config:
        orm_mode = True


class OutputLegalRequirement(BaseModel):
    title: str
    content: str
    accept_text: str
    button_text: str

    class Config:
        orm_mode = True


class OutputLegalRequirementEvent(BaseModel):
    actor: Optional[OutputRlcUser]
    text: Optional[str]
    accepted: bool
    created: datetime

    class Config:
        orm_mode = True


class OutputLegalRequirementUser(BaseModel):
    legal_requirement: OutputLegalRequirement
    rlc_user_id: int
    accepted: bool
    id: int
    events_list: List[OutputLegalRequirementEvent]

    class Config:
        orm_mode = True


class InputLegalRequirementEventCreate(BaseModel):
    id: int
