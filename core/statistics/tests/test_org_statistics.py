import pytest
from django.test import Client

from core.data_sheets.models import DataSheetTemplate
from core.org.models import Org
from core.tests import test_helpers as test_helpers


@pytest.fixture
def user(db):
    org = Org.objects.create(name="Test RLC")
    user_1 = test_helpers.create_org_user(org=org)
    user_2 = test_helpers.create_org_user(email="dummy2@law-orga.de", org=org)
    test_helpers.create_org_user(email="dummy3@law-orga.de", org=org)
    org.generate_keys()
    template = DataSheetTemplate.objects.create(org=org, name="Record Template")
    test_helpers.create_data_sheet(
        template=template, users=[user_1["user"], user_2["user"]]
    )
    test_helpers.create_data_sheet(
        template=template, users=[user_1["user"], user_2["user"]]
    )
    yield user_1


def test_records_created_and_closed_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/statistics/org/records_created_and_closed/")
    response_data = response.json()
    assert response.status_code == 200 and response_data["data"][0]["created"] == 2
