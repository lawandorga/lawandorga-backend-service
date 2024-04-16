from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InputCreateRecord(BaseModel):
    token: str
    template: Optional[int] = None


class OutputCreateRecord(BaseModel):
    folder_uuid: UUID
    record_uuid: UUID | None = None
