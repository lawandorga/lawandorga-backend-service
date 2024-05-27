import pytest

from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS
from core.records.models import RecordsAccessRequest, RecordsRecord
from core.records.use_cases.access import create_access_request, grant_access_request
from core.seedwork import test_helpers
from core.seedwork.domain_layer import DomainError


@pytest.fixture
def org():
    yield test_helpers.create_raw_org()


@pytest.fixture
def user(org):
    yield test_helpers.create_raw_org_user(org)


@pytest.fixture
def view(org, user):
    folder = test_helpers.create_raw_folder(user)
    yield RecordsRecord.create("Dummy's Record", user, folder, pk=1)


@pytest.fixture
def another_user(org):
    yield test_helpers.create_raw_org_user(
        org=org, email="tester@law-orga.de", name="Mr. Tester", user_pk=2, pk=2
    )


@pytest.fixture
def record(org, user):
    folder = test_helpers.create_raw_folder(user)
    record = RecordsRecord.create(token="AZ-TEST", user=user, folder=folder, pk=1)
    yield record


def test_grant_access(record, another_user, user):
    access = RecordsAccessRequest.create(record, another_user)
    access.grant(user)
    assert access.state == "gr"


def test_decline_access(record, another_user, user):
    access = RecordsAccessRequest.create(record, another_user)
    access.decline(user)
    assert access.state == "de"


def test_access_raises(record, another_user, user):
    access = RecordsAccessRequest.create(record, another_user)
    with pytest.raises(DomainError):
        access.grant(another_user)
    access.grant(user)
    with pytest.raises(DomainError):
        access.grant(user)
    with pytest.raises(DomainError):
        access.decline(user)


def test_access_works(db):
    full_record = test_helpers.create_record()
    record = full_record["record"]
    user = full_record["user"]

    full_other_user = test_helpers.create_org_user(
        email="tester@law-orga.de", rlc=user.org
    )
    other_user = full_other_user["rlc_user"]

    create_access_request(other_user, "testing", record.uuid)

    access = RecordsAccessRequest.objects.get(requestor=other_user, record=record)
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS)

    assert not RecordsRecord.objects.get(pk=record.pk).folder.has_access(other_user)
    grant_access_request(user, access.uuid)
    assert RecordsRecord.objects.get(pk=record.pk).folder.has_access(other_user)


def test_access_grant_works_if_access_already_exists(db):
    full_record = test_helpers.create_record()
    record = full_record["record"]
    user = full_record["user"]
    folder = full_record["folder"]

    full_other_user = test_helpers.create_org_user(
        email="tester@law-orga.de", rlc=user.org
    )
    other_user = full_other_user["rlc_user"]

    folder.grant_access(other_user, user)
    access = RecordsAccessRequest.create(record, user, "needs to go")
    access.save()
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS)

    grant_access_request(user, access.uuid)
