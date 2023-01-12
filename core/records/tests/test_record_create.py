import pytest

from core.records.models import Record
from core.records.use_cases.record import (
    create_a_record_and_a_folder,
    create_a_record_within_a_folder,
)
from core.seedwork.use_case_layer import UseCaseError
from core.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)


def test_create_within_folder(user, record_template, folder):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_record_within_a_folder(
        user["rlc_user"],
        "record123",
        folder=folder.uuid,
        template=record_template["template"].pk,
    )


def test_create_record_and_folder(user, record_template, folder):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_record_and_a_folder(
        user["rlc_user"],
        name="My folder that contains a record",
        template=record_template["template"].pk,
    )


def test_create_no_permission(user, record_template, folder):
    with pytest.raises(UseCaseError):
        create_a_record_within_a_folder(
            user["rlc_user"],
            "record123",
            folder=folder.uuid,
            template=record_template["template"].pk,
        )


def test_records_are_added_to_folder(user, record_template, folder, folder_repo):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_record_within_a_folder(
        user["rlc_user"],
        "record123",
        folder=folder.uuid,
        template=record_template["template"].pk,
    )
    create_a_record_within_a_folder(
        user["rlc_user"],
        "record123",
        folder=folder.uuid,
        template=record_template["template"].pk,
    )
    f = folder_repo.retrieve(folder.org_pk, folder.uuid)
    assert 2 == len(f.items)


def test_no_access_to_folder(user, record_template, folder, another_user):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    with pytest.raises(UseCaseError):
        create_a_record_within_a_folder(
            another_user["rlc_user"],
            "record123",
            folder=folder.uuid,
            template=record_template["template"].pk,
        )


def test_grant_to_users_with_general_permission(
    user, folder, record_template, another_user, folder_repo
):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["rlc_user"].grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    assert folder.has_access(user["rlc_user"]) and not folder.has_access(
        another_user["rlc_user"]
    )

    record_id = create_a_record_within_a_folder(
        user["rlc_user"],
        "record123",
        folder=folder.uuid,
        template=record_template["template"].pk,
    )
    folder_uuid = Record.objects.get(id=record_id).folder_uuid

    assert folder_repo.retrieve(folder.org_pk, folder_uuid).has_access(
        another_user["rlc_user"]
    )


def test_grant_to_users_with_general_permission_two(
    user, folder, record_template, another_user, folder_repo
):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["rlc_user"].grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    assert folder.has_access(user["rlc_user"]) and not folder.has_access(
        another_user["rlc_user"]
    )

    record_id = create_a_record_and_a_folder(
        user["rlc_user"],
        "record123",
        template=record_template["template"].pk,
    )
    folder_uuid = Record.objects.get(id=record_id).folder_uuid

    assert folder_repo.retrieve(folder.org_pk, folder_uuid).has_access(
        another_user["rlc_user"]
    )
