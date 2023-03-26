from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.records.models.setting import RecordsView
from core.records.use_cases.finders import find_view_by_uuid
from core.seedwork.use_case_layer import use_case


@use_case
def create_view(__actor: RlcUser, name: str, columns: list[str]):
    view = RecordsView.create(name=name, user=__actor, columns=columns)
    view.save()


@use_case
def update_view(__actor: RlcUser, uuid: UUID, name: str, columns: list[str]):
    view = find_view_by_uuid(__actor, uuid)
    view.update_information(name=name, columns=columns)
    view.save()


@use_case
def delete_view(__actor: RlcUser, uuid: UUID):
    view = find_view_by_uuid(__actor, uuid)
    view.delete()
