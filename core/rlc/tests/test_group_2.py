import pytest

from core.seedwork import test_helpers


@pytest.fixture
def group():
    user = test_helpers.create_raw_org_user()
    group = test_helpers.create_raw_group(org=user.org)
    yield group


def test_group_update_information(group):
    group.update_information(name="New Name", description="New Description")
    assert group.name == "New Name" and group.description == "New Description"
    group.update_information(None, None)
    assert group.name == "New Name" and group.description == "New Description"
