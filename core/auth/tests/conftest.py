import pytest

from core.rlc.models import Org


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org
