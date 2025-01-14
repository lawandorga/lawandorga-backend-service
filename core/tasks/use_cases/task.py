from datetime import datetime
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
def delete_task(__actor: OrgUser, task_uuid):
    task = task_from_uuid(__actor, task_uuid)
    task.delete()
