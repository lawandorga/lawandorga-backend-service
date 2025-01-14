# TODO: rename todos in tasks

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router
from core.todos.models.todos import Todo


class InputTasks(BaseModel):
    id: int


# do we want to split into two models, one with creator, one with assignee?
class OutputTask(BaseModel):
    uuid: UUID
    creator_id: int
    assignee_id: int
    title: str
    description: str
    page_url: str
    is_done: bool
    deadline: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


router = Router()


@router.get(
    url="own/",
    output_schema=list[OutputTask],
)
def query__own_tasks(rlc_user: OrgUser):
    tasks = Todo.objects.filter(assignee=rlc_user)
    return tasks


@router.get(
    url="created/",
    output_schema=list[OutputTask],
)
def query__created_tasks(rlc_user: OrgUser):
    tasks = Todo.objects.filter(creator=rlc_user)
    return tasks
