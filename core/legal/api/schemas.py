from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OutputLegalRequirementEvent(BaseModel):
    actor: str
    text: Optional[str]
    accepted: bool
    created: datetime

    class Config:
        orm_mode = True


class OutputLegalRequirement(BaseModel):
    id: int
    title: str
    content: str
    accept_text: str
    button_text: str
    events_of_user: list[OutputLegalRequirementEvent]
    accepted_of_user: bool

    class Config:
        orm_mode = True


class InputLegalRequirementEventCreate(BaseModel):
    id: int
