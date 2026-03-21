from datetime import datetime
from typing import Optional
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.seedwork.use_case_layer import use_case
from core.tasks.models.task import Task
from core.tasks.use_cases.finder import task_from_uuid, tasks_from_uuids


@use_case
def mark_tasks_as_done(__actor: OrgUser, task_uuids: list[UUID]):
    tasks = tasks_from_uuids(__actor, task_uuids)
    for task in tasks:
        task.mark_as_done()
    Task.objects.bulk_update(tasks, ["is_done"])


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
    is_done: Optional[bool] = None,
    deadline: Optional[datetime] = None,
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
    if is_done is not None:
        task.is_done = is_done
    task.deadline = deadline

    task.save()

    if assignee_ids is not None:
        assignees = OrgUser.objects.filter(id__in=assignee_ids)
        task.assignees.set(assignees)


@use_case
def delete_task(__actor: OrgUser, task_uuid):
    task = task_from_uuid(__actor, task_uuid)
    task.delete()
