import pytest

from core.rlc.models import Org
from core.seedwork import test_helpers


@pytest.fixture
def org() -> Org:
    org = test_helpers.create_raw_org()
    yield org


@pytest.fixture
def user(org):
    user = test_helpers.create_raw_org_user(org)
    yield user


@pytest.fixture
def folder(user):
    folder = test_helpers.create_raw_folder(user)
    yield folder
