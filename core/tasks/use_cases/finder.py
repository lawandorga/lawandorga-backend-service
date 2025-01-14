from uuid import UUID

from core.auth.models import OrgUser
from core.seedwork.use_case_layer import finder_function
from core.tasks.models.task import Task


@finder_function
def task_from_uuid(_: OrgUser, uuid: UUID) -> Task:
    return Task.objects.get(uuid=uuid)


@finder_function
def tasks_from_uuids(_: OrgUser, uuids: list[UUID]) -> list[Task]:
    return list(Task.objects.filter(uuid__in=uuids))
