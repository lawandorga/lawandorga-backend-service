from datetime import datetime
from typing import Optional
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.seedwork.use_case_layer import use_case
from core.tasks.models.task import Task
from core.tasks.use_cases.finder import task_from_uuid


@use_case
def create_task(
    __actor: OrgUser,
    assignee_ids: list[int],
    title: str,
    description: str = "",
    page_url: str = "",
    deadline: Optional[datetime] = None,
):
    Task.create(
        __actor, assignee_ids, title, description, page_url, deadline, save=True
    )


@use_case
def update_task(
    __actor: OrgUser,
    task_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    page_url: Optional[str] = None,
    assignee_ids: Optional[list[int]] = None,
    progress: Optional[int] = None,
    priority: Optional[str] = None,
    deadline: Optional[datetime] = None,
    comment: Optional[str] = None,
):
    task = Task.objects.get(uuid=task_id)

    if task.creator != __actor and not task.assignees.filter(pk=__actor.pk).exists():
        raise PermissionError("You are not allowed to update this task.")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if page_url is not None:
        task.page_url = page_url
    if progress is not None:
        task.progress = progress
    if priority is not None:
        task.priority = priority
    if comment:
        task.comments = task.comments + [
            {"email": __actor.email, "comment": comment}
        ]
    task.deadline = deadline

    task.save()

    if assignee_ids is not None:
        assignees = OrgUser.objects.filter(id__in=assignee_ids)
        task.assignees.set(assignees)


@use_case
def delete_task(__actor: OrgUser, task_uuid):
    task = task_from_uuid(__actor, task_uuid)
    task.delete()
