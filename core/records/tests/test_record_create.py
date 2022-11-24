import pytest

from core.records.use_cases.record import create_a_record
from core.seedwork.use_case_layer import UseCaseError
from core.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)


def test_create(user, record_template, folder):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_record(
        user["rlc_user"], folder=folder.pk, template=record_template["template"].pk
    )


def test_create_no_permission(user, record_template, folder):
    with pytest.raises(UseCaseError):
        create_a_record(
            user["rlc_user"], folder=folder.pk, template=record_template["template"].pk
        )


def test_upgrade_amount_stays_the_same(user, record_template, folder, folder_repo):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    create_a_record(
        user["rlc_user"], folder=folder.pk, template=record_template["template"].pk
    )
    create_a_record(
        user["rlc_user"], folder=folder.pk, template=record_template["template"].pk
    )
    assert len(folder_repo.retrieve(folder.org_pk, folder.pk).upgrades) == 1


def test_no_access_to_folder(user, record_template, folder, another_user):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    with pytest.raises(UseCaseError):
        create_a_record(
            another_user["rlc_user"],
            folder=folder.pk,
            template=record_template["template"].pk,
        )


def test_grant_to_users_with_general_permission(
    user, folder, record_template, another_user, folder_repo
):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    another_user["rlc_user"].grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)
    create_a_record(
        user["rlc_user"], folder=folder.pk, template=record_template["template"].pk
    )
    assert folder_repo.retrieve(folder.org_pk, folder.pk).has_access(
        another_user["rlc_user"]
    )
