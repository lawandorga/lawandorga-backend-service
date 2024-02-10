from core.records.use_cases.access import (
    create_access_request,
    decline_access_request,
    grant_access_request,
)
from core.records.use_cases.deletion import (
    accept_deletion_request,
    create_deletion_request,
    decline_deletion_request,
)
from core.records.use_cases.record import change_record_token
from core.records.use_cases.setting import create_view, delete_view, update_view

USECASES = {
    "records/create_deletion_request": create_deletion_request,
    "records/accept_deletion_request": accept_deletion_request,
    "records/decline_deletion_request": decline_deletion_request,
    "records/change_token": change_record_token,
    "records/create_view": create_view,
    "records/update_view": update_view,
    "records/delete_view": delete_view,
    "records/create_access_request": create_access_request,
    "records/grant_access_request": grant_access_request,
    "records/decline_access_request": decline_access_request,
}
