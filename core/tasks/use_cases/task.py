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
    creator: OrgUser,
    assignee: OrgUser,
    title: str,
    description: str,
    page_url: str,
    updated_at: str,
    deadline: datetime,
):
    Task.create(creator, assignee, title, description, page_url, updated_at, deadline)


@use_case
def update_task(
    task_id: UUID,
    updater: OrgUser,
    title: Optional[str] = None,
    description: Optional[str] = None,
    page_url: Optional[str] = None,
    assignee: Optional[OrgUser] = None,
    is_done: Optional[bool] = None,
    deadline: Optional[datetime] = None,
):
    task = Task.objects.get(uuid=task_id)

    if task.creator != updater and task.assignee != updater:
        raise PermissionError("You are not allowed to update this task.")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if page_url is not None:
        task.page_url = page_url
    if assignee is not None:
        task.assignee = assignee
    if is_done is not None:
        task.is_done = is_done
    if deadline is not None:
        task.deadline = deadline

    task.save()


@use_case
def delete_task(__actor: OrgUser, task_uuid):
    task = task_from_uuid(__actor, task_uuid)
    task.delete()
