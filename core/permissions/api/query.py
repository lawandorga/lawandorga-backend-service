from pydantic import BaseModel

from core.permissions.models import Permission
from core.seedwork.api_layer import Router

router = Router()


class OutputPermission(BaseModel):
    id: int
    name: str
    description: str
    recommended_for: str

    class Config:
        orm_mode = True


@router.get("permissions/", output_schema=list[OutputPermission])
def query__permissions():
    return list(Permission.objects.all())
