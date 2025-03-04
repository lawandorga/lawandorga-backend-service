import json

import pytest
from django.test import Client
from django.utils import timezone

from core.data_sheets.models import (
    DataSheetStateEntry,
    DataSheetStateField,
    DataSheetTemplate,
)
from core.org.models import Org
from core.seedwork import test_helpers as data


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_org_user(rlc=rlc)
    statistics_user = data.create_statistics_user(
        email="statistics@law-orga.de", name="Mr. Statistics"
    )
    rlc.generate_keys()
    template = DataSheetTemplate.objects.create(rlc=rlc, name="Record Template")
    field = DataSheetStateField.objects.create(
        template=template, options=["Open", "Closed"]
    )
    record1 = data.create_data_sheet(template=template, users=[user_1["user"]])
    DataSheetStateEntry.objects.create(
        field=field, record=record1["record"], value="Closed", closed_at=timezone.now()
    )
    record2 = data.create_data_sheet(template=template, users=[user_1["user"]])
    DataSheetStateEntry.objects.create(
        field=field, record=record2["record"], value="Closed"
    )
    yield statistics_user


def test_records_closed_statistic(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/statistics/record/records_closed_statistic/")
    response_data = response.json()
    assert response.status_code == 200 and len(response_data) == 2


def test_records_field_statistic(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/statistics/record/record_fields_amount/")
    assert response.status_code == 200


def test_records_dynamic_statistic(user, db):
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/statistics/record/dynamic/",
        data=json.dumps({"field_1": "Token", "value_1": "%", "field_2": "Token"}),
        content_type="application/json",
    )
    assert response.status_code == 200
