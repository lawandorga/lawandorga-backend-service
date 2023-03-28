import json
from typing import cast

from django.test import Client

from core.folders.domain.repositiories.folder import FolderRepository
from core.records.use_cases.record import create_record
from core.seedwork import test_helpers
from core.seedwork.repository import RepositoryWarehouse
from core.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)


def test_record_creation(db):
    full_user = test_helpers.create_rlc_user()
    client = Client()
    client.login(**full_user)
    response = client.post(
        "/api/records/v2/records/",
        data=json.dumps({"token": "AZ-001"}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_grant_to_users_with_general_permission(db):
    full_user = test_helpers.create_rlc_user()
    user = full_user["rlc_user"]
    full_another_user = test_helpers.create_rlc_user(
        email="tester@law-orga.de", rlc=user.org
    )
    another_user = full_another_user["rlc_user"]

    user.grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user.grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    folder_uuid = create_record(user, "AZ-TEST")

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository.IDENTIFIER))
    folder = r.retrieve(user.org_id, folder_uuid)

    assert folder.has_access(another_user)
