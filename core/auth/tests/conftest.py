import pytest

from core.org.models import Org


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org
