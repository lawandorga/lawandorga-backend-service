import pytest
from django.test import Client

from core.data_sheets.models import DataSheetTemplate
from core.rlc.models import Org
from core.seedwork import test_helpers as data


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_rlc_user(rlc=rlc)
    user_2 = data.create_rlc_user(email="dummy2@law-orga.de", rlc=rlc)
    data.create_rlc_user(email="dummy3@law-orga.de", rlc=rlc)
    rlc.generate_keys()
    template = DataSheetTemplate.objects.create(rlc=rlc, name="Record Template")
    data.create_data_sheet(template=template, users=[user_1["user"], user_2["user"]])
    data.create_data_sheet(template=template, users=[user_1["user"], user_2["user"]])
    yield user_1


def test_records_created_and_closed_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/statistics/org/records_created_and_closed/")
    response_data = response.json()
    assert response.status_code == 200 and response_data[0]["created"] == 2
