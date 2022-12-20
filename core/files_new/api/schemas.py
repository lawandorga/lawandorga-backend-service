from typing import Any
from uuid import UUID

from pydantic import BaseModel


class InputUploadFile(BaseModel):
    file: Any
    folder: UUID
