import pytest

from core.records.models import RecordsDeletion
from core.records.models.record import RecordsRecord
from core.seedwork import test_helpers
from core.seedwork.domain_layer import DomainError


@pytest.fixture
def org():
    yield test_helpers.create_raw_org()


@pytest.fixture
def user(org):
    yield test_helpers.create_raw_org_user(org)


@pytest.fixture
def record(user):
    folder = test_helpers.create_raw_folder(user)
    yield RecordsRecord.create("Dummy's Record", user, folder, pk=1)


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


def test_access_raises(record, another_user, user):
    access = RecordsDeletion.create(record, another_user)
    access.accept(user)
    with pytest.raises(DomainError):
        access.accept(user)
    with pytest.raises(DomainError):
        access.decline(user)
