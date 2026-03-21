from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db.models import Q
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router
from core.tasks.models.task import Task


class InputTasks(BaseModel):
    id: int


class OutputTask(BaseModel):
    uuid: UUID
    creator_id: int
    creator_name: str
    assignee_ids: list[int]
    assignee_names: list[str]
    title: str
    description: str
    page_url: str
    is_done: bool
    deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


router = Router()


@router.get(
    url="",
    output_schema=list[OutputTask],
)
def query__tasks(org_user: OrgUser):
    tasks = Task.objects.filter(Q(creator=org_user) | Q(assignees=org_user)).distinct()
    return tasks
