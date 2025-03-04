import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.models import Org
from core.seedwork import test_helpers as data


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def user(db, org):
    user_1 = data.create_org_user(rlc=org)
    org.generate_keys()
    yield user_1


@pytest.fixture
def another_user(db, user, org):
    user_2 = data.create_org_user(rlc=org, email="test@law-orga.de")
    org.accept_member(
        user["org_user"],
        user_2["org_user"],
    )
    yield user_2


@pytest.fixture
def record_template(db, org):
    template = data.create_record_template(org)
    yield template


@pytest.fixture
def record(db, org, user, record_template):
    record = data.create_data_sheet(record_template["template"], [user["user"]])
    yield record["record"]


@pytest.fixture
def folder(db, org, user):
    folder = Folder.create(name="New Folder", org_pk=org.pk)
    folder.grant_access(to=user["org_user"])
    r = DjangoFolderRepository()
    r.save(folder)
    yield r.retrieve(org.pk, folder.uuid)


@pytest.fixture
def folder_repo():
    yield DjangoFolderRepository()
