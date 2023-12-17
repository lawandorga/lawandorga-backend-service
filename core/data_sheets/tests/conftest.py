from typing import cast

import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.models import Org
from core.seedwork import test_helpers as data
from core.seedwork.repository import RepositoryWarehouse

EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
RepositoryWarehouse.add_repository(DjangoFolderRepository)


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
        user["rlc_user"],
        user_2["rlc_user"],
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
    folder.grant_access(to=user["rlc_user"])
    r = DjangoFolderRepository()
    r.save(folder)
    yield r.retrieve(org.pk, folder.uuid)


@pytest.fixture
def folder_repo():
    yield cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
