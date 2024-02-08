from core.records.use_cases.deletion import (
    accept_deletion_request,
    create_deletion_request,
    decline_deletion_request,
)

USECASES = {
    "records/create_deletion_request": create_deletion_request,
    "records/accept_deletion_request": accept_deletion_request,
    "records/decline_deletion_request": decline_deletion_request,
}
