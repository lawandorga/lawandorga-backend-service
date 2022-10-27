import pytest
from django.test import Client

from core.records.models import RecordTemplate
from core.rlc.models import Org
from core.seedwork import test_helpers as data
from core.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_rlc_user(rlc=rlc)
    user_2 = data.create_rlc_user(email="dummy2@law-orga.de", rlc=rlc)
    user_3 = data.create_rlc_user(email="dummy3@law-orga.de", rlc=rlc)
    statistics_user = data.create_statistics_user(
        email="statistics@law-orga.de", name="Mr. Statistics"
    )
    rlc.generate_keys()
    template = RecordTemplate.objects.create(rlc=rlc, name="Record Template")
    data.create_record(template=template, users=[user_1["user"], user_2["user"]])
    data.create_record(template=template, users=[user_1["user"], user_2["user"]])
    user_3["rlc_user"].grant(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)
    yield statistics_user


def test_users_with_missing_record_keys_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/statistics/error/users_with_missing_record_keys/")
    response_data = response.json()
    assert response.status_code == 200 and len(response_data) == 1
