from typing import Literal

from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router

router = Router()


class OutputKey(BaseModel):
    id: int
    correct: bool
    source: Literal["RECORD", "ORG", "FOLDER", "USER", "GROUP"]
    information: str
    group_id: int | None

    model_config = ConfigDict(from_attributes=True)


@router.get(output_schema=list[OutputKey])
def list_keys(rlc_user: OrgUser):
    return rlc_user.keys
