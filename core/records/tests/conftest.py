import pytest
from core.models import Org
from core.seedwork import test_helpers as data


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def user(db, org):
    user_1 = data.create_rlc_user(rlc=org)
    org.generate_keys()
    yield user_1


@pytest.fixture
def record(db, org, user):
    template = data.create_record_template(org)
    record = data.create_record(template["template"], [user["user"]])
    yield record["record"]
