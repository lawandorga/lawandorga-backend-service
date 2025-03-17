from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router
from core.tasks.models.task import Task


class InputTasks(BaseModel):
    id: int


# do we want to split into two models, one with creator, one with assignee?
class OutputTask(BaseModel):
    uuid: UUID
    creator_id: int
    creator_name: str
    assignee_id: int
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
    url="own/",
    output_schema=list[OutputTask],
)
def query__own_tasks(org_user: OrgUser):
    tasks = Task.objects.filter(assignee=org_user)
    return tasks


@router.get(
    url="created/",
    output_schema=list[OutputTask],
)
def query__created_tasks(org_user: OrgUser):
    tasks = Task.objects.filter(creator=org_user)
    return tasks
