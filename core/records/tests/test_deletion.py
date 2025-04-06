import pytest

from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS
from core.records.models import RecordsDeletion
from core.records.models.record import RecordsRecord
from core.records.use_cases.deletion import accept_deletion_request
from core.seedwork import test_helpers
from core.seedwork.domain_layer import DomainError
from messagebus.domain.collector import EventCollector


@pytest.fixture
def org():
    yield test_helpers.create_raw_org()


@pytest.fixture
def user(org):
    yield test_helpers.create_raw_org_user(org)


@pytest.fixture
def record(user):
    folder = test_helpers.create_raw_folder(user)
    yield RecordsRecord.create(
        "Dummy's Record", user, folder, pk=1, collector=EventCollector()
    )


@pytest.fixture
def another_user(org):
    yield test_helpers.create_raw_org_user(
        org=org, email="tester@law-orga.de", name="Mr. Tester", user_pk=2, pk=2
    )


def test_grant_access(record, another_user, user):
    access = RecordsDeletion.create(record, another_user)
    access.accept(user)
    assert access.state == "gr"


def test_decline_access(record, another_user, user):
    access = RecordsDeletion.create(record, another_user)
    access.decline(user)
    assert access.state == "de"


def test_deletion_raises(record, another_user, user):
    access = RecordsDeletion.create(record, another_user)
    access.accept(user)
    with pytest.raises(DomainError):
        access.accept(user)
    with pytest.raises(DomainError):
        access.decline(user)


def test_deletion_works(db):
    full_user = test_helpers.create_org_user()
    user = full_user["org_user"]
    record = test_helpers.create_record(user=user)["record"]
    deletion = RecordsDeletion.create(record, user)
    deletion.save()
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS)
    assert RecordsRecord.objects.filter(pk=record.pk).count() == 1
    accept_deletion_request(user, deletion.uuid)
    assert RecordsRecord.objects.filter(pk=record.pk).count() == 0
