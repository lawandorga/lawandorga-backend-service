import pytest

from core.seedwork import test_helpers
from core.seedwork.domain_layer import DomainError


@pytest.fixture
def template():
    user = test_helpers.create_raw_org_user()
    yield test_helpers.create_raw_template(org=user.org)


def test_template_show_options(db, template):
    assert template.show_options == ["Created", "Updated", "Name"]
    with pytest.raises(DomainError):
        template.update_show(["Test"])
    template.update_show(["Name", "Created"])
