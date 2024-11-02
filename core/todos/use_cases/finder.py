from uuid import UUID

from core.auth.models import OrgUser
from core.seedwork.use_case_layer import finder_function
from core.todos.models.todos import Todo


@finder_function
def todo_from_uuid(_: OrgUser, uuid: UUID) -> Todo:
    return Todo.objects.get(uuid=uuid)


@finder_function
def todos_from_uuids(_: OrgUser, uuids: list[UUID]) -> list[Todo]:
    return list(Todo.objects.filter(uuid__in=uuids))
