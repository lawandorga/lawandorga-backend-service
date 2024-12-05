# TODO: rename todos in tasks

from datetime import datetime
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from pydantic import BaseModel, ConfigDict

from core.auth.models.user import UserProfile
from core.seedwork.api_layer import Router
from core.todos.models.todos import Todo


class InputTasks(BaseModel):
    uuid: UUID

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# do we want to split into two models, one with creator, one with assignee?
class OutputTask(BaseModel):
    uuid: UUID
    creator: UserProfile
    assignee: UserProfile
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
    url="<uuid:user>/own/",
    output_schema=list[OutputTask],
)
def query__own_tasks(user: UserProfile, data: InputTasks):
    try:
        tasks = Todo.objects.filter(assignee=user).get(uuid=data.uuid)
    except ObjectDoesNotExist:
        tasks = []
    return "data.uuid"


@router.get(
    url="<uuid:user>/created/",
    output_schema=list[OutputTask],
)
def query__created_tasks():
    pass
