from core.auth.models import RlcUser
from core.data_sheets.models import RecordAccess
from core.data_sheets.use_cases.finders import access_from_id, record_from_id
from core.seedwork.use_case_layer import use_case
from core.static import PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS


@use_case
def create_access_request(__actor: RlcUser, explanation: str, record_id: int):
    record = record_from_id(__actor, record_id)
    access = RecordAccess.create(record, __actor, explanation)
    access.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS])
def grant_access_request(__actor: RlcUser, access_id: int):
    access = access_from_id(__actor, access_id)
    access.grant(__actor)
    access.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS])
def decline_access_request(__actor: RlcUser, access_id: int):
    access = access_from_id(__actor, access_id)
    access.decline(__actor)
    access.save()
