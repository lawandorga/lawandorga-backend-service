from uuid import UUID

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.org.models.group import Group
from core.seedwork.message_layer import MessageBusActor
from core.seedwork.use_case_layer import finder_function


@finder_function
def folder_from_uuid(actor: OrgUser | MessageBusActor, v: UUID) -> Folder:
    repository = DjangoFolderRepository()
    org_id: int = actor.org_id  # type: ignore
    folder = repository.retrieve(org_pk=org_id, uuid=v)
    return folder


@finder_function
def org_user_from_uuid(actor: OrgUser | MessageBusActor, v: UUID) -> OrgUser:
    return OrgUser.objects.get(org__id=actor.org_id, uuid=v)


@finder_function
def group_from_uuid(actor: OrgUser, v: UUID) -> Group:
    return Group.objects.get(org__id=actor.org_id, uuid=v)
