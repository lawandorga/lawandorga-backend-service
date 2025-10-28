import pytest

from core.data_sheets.models import DataSheet
from core.data_sheets.use_cases.sheet import (
    create_a_data_sheet_within_a_folder,
    create_data_sheet_and_folder,
)
from core.permissions.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)
from core.seedwork.use_case_layer import UseCaseError


def test_create_within_folder(user, record_template, folder):
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_data_sheet_within_a_folder(
        user["org_user"],
        "record123",
        folder_uuid=folder.uuid,
        template_id=record_template["template"].pk,
    )


def test_create_record_and_folder(user, record_template, folder):
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_data_sheet_and_folder(
        user["org_user"],
        name="My folder that contains a record",
        template_id=record_template["template"].pk,
    )


def test_create_no_permission(user, record_template, folder):
    with pytest.raises(UseCaseError):
        create_a_data_sheet_within_a_folder(
            user["org_user"],
            "record123",
            folder_uuid=folder.uuid,
            template_id=record_template["template"].pk,
        )


def test_records_are_added_to_folder(user, record_template, folder, folder_repo):
    f = folder_repo.retrieve(folder.org_pk, folder.uuid)
    assert 0 == len(f.items)
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_data_sheet_within_a_folder(
        user["org_user"],
        "record123",
        folder_uuid=folder.uuid,
        template_id=record_template["template"].pk,
    )
    f = folder_repo.retrieve(folder.org_pk, folder.uuid)
    assert 1 == len(f.items)
    create_a_data_sheet_within_a_folder(
        user["org_user"],
        "record123",
        folder_uuid=folder.uuid,
        template_id=record_template["template"].pk,
    )
    f = folder_repo.retrieve(folder.org_pk, folder.uuid)
    assert 2 == len(f.items)


def test_no_access_to_folder(user, record_template, folder, another_user):
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    with pytest.raises(UseCaseError):
        create_a_data_sheet_within_a_folder(
            another_user["org_user"],
            "record123",
            folder_uuid=folder.uuid,
            template_id=record_template["template"].pk,
        )


def test_grant_to_users_with_general_permission(
    user, folder, record_template, another_user, folder_repo
):
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["org_user"].grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    assert folder.has_access(user["org_user"]) and not folder.has_access(
        another_user["org_user"]
    )

    record = create_a_data_sheet_within_a_folder(
        user["org_user"],
        "record123",
        folder_uuid=folder.uuid,
        template_id=record_template["template"].pk,
    )

    assert folder_repo.retrieve(folder.org_pk, record.folder_uuid).has_access(
        another_user["org_user"]
    )


def test_grant_to_users_with_general_permission_two(
    user, folder, record_template, another_user, folder_repo
):
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["org_user"].grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    assert folder.has_access(user["org_user"]) and not folder.has_access(
        another_user["org_user"]
    )

    record = create_data_sheet_and_folder(
        user["org_user"],
        "record123",
        template_id=record_template["template"].pk,
    )
    folder_uuid = DataSheet.objects.get(uuid=record.uuid).folder_uuid

    assert folder_repo.retrieve(folder.org_pk, folder_uuid).has_access(
        another_user["org_user"]
    )
