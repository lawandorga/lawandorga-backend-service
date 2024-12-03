from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.seedwork.use_case_layer import use_case
from core.todos.models.todos import Todo
from core.todos.use_cases.finder import todo_from_uuid, todos_from_uuids

if TYPE_CHECKING:
    from ...auth.models import UserProfile


@use_case
def mark_todos_as_done(__actor: OrgUser, todos_uuids: list[UUID]):
    todos = todos_from_uuids(__actor, todos_uuids)
    for todo in todos:
        todo.mark_as_done()
    Todo.objects.bulk_update(todos, ["is_done"])


@use_case
def create_todo(
    creator: UserProfile,
    assignee: UserProfile,
    title: str,
    description: str,
    page_url: str,
    updated_at: str,
    deadline: datetime,
):
    Todo.create(creator, assignee, title, description, page_url, updated_at, deadline)


@use_case
def delete_todo(__actor: OrgUser, todo_uuid):
    todo = todo_from_uuid(__actor, todo_uuid)
    todo.delete()
