import json
from typing import cast

from django.test import Client

from core.data_sheets.models.data_sheet import DataSheet
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)
from core.records.models.deletion import RecordsDeletion
from core.records.models.record import RecordsRecord
from core.records.use_cases.deletion import accept_deletion_request
from core.records.use_cases.record import create_record
from core.seedwork import test_helpers
from core.seedwork.repository import RepositoryWarehouse


def test_record_creation(db):
    full_user = test_helpers.create_org_user()
    user = full_user["rlc_user"]
    user.grant(PERMISSION_RECORDS_ADD_RECORD)
    client = Client()
    client.login(**full_user)
    response = client.post(
        "/api/records/records/",
        data=json.dumps({"token": "AZ-001"}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_grant_to_users_with_general_permission(db):
    full_user = test_helpers.create_org_user()
    user = full_user["rlc_user"]
    full_another_user = test_helpers.create_org_user(
        email="tester@law-orga.de", rlc=user.org
    )
    another_user = full_another_user["rlc_user"]

    user.grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user.grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    folder_uuid = create_record(user, "AZ-TEST")

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository.IDENTIFIER))
    folder = r.retrieve(user.org_id, folder_uuid)

    assert folder.has_access(another_user)


def test_delete_deletes_data_sheet_as_well(db):
    full_user = test_helpers.create_org_user()
    user = full_user["rlc_user"]
    template = test_helpers.create_record_template(user.org)["template"]
    user.grant(PERMISSION_RECORDS_ADD_RECORD)
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS)
    client = Client()
    client.login(**full_user)
    TOKEN = "AZ-001"
    data_sheet_count = DataSheet.objects.count()
    response = client.post(
        "/api/records/records/",
        data=json.dumps({"token": TOKEN, "template": template.pk}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert DataSheet.objects.count() == data_sheet_count + 1
    record = RecordsRecord.objects.get(name=TOKEN)
    deletion = RecordsDeletion.create(record=record, user=user)
    deletion.save()
    accept_deletion_request(user, deletion.uuid)
    assert DataSheet.objects.count() == data_sheet_count
