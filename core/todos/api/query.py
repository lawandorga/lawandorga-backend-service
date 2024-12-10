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
    url="<int:id>/own/",
    output_schema=list[OutputTask],
)
def query__own_tasks(data: InputTasks):
    org_user = OrgUser.objects.get(id=data.id)
    tasks = Todo.objects.filter(assignee=org_user)

    serialized_tasks = [
        OutputTask(
            uuid=task.uuid,
            creator_id=task.creator.pk,
            assignee_id=task.assignee.pk,
            title=task.title,
            description=task.description,
            page_url=task.page_url,
            is_done=task.is_done,
            deadline=task.deadline,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]
    return serialized_tasks


@router.get(
    url="<int:id>/created/",
    output_schema=list[OutputTask],
)
def query__created_tasks(data: InputTasks):
    org_user = OrgUser.objects.get(id=data.id)
    tasks = Todo.objects.filter(creator=org_user)

    serialized_tasks = [
        OutputTask(
            uuid=task.uuid,
            creator_id=task.creator.pk,
            assignee_id=task.assignee.pk,
            title=task.title,
            description=task.description,
            page_url=task.page_url,
            is_done=task.is_done,
            deadline=task.deadline,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]
    return serialized_tasks
