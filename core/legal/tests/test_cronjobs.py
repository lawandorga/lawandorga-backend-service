import pytest

from core.models import Org
from core.seedwork import test_helpers

from ..cronjobs import create_legal_requirements_for_users
from ..models import LegalRequirement, LegalRequirementUser


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user = test_helpers.create_rlc_user(rlc=rlc)
    yield user


@pytest.fixture()
def legal_requirement(user):
    LegalRequirement.objects.create(
        title="Test", content="Accept this please", accept_required=True
    )


def test_legal_requirement_user_is_created(user, legal_requirement):
    count = LegalRequirementUser.objects.count()
    create_legal_requirements_for_users()
    assert LegalRequirementUser.objects.count() > count
