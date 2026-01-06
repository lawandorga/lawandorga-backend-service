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
from core.seedwork import test_helpers as test_helpers


@pytest.fixture
def user(db):
    org = Org.objects.create(name="Test RLC")
    user_1 = test_helpers.create_org_user(org=org)
    statistics_user = test_helpers.create_statistics_user(
        email="statistics@law-orga.de", name="Mr. Statistics"
    )
    org.generate_keys()
    template = DataSheetTemplate.objects.create(org=org, name="Record Template")
    field = DataSheetStateField.objects.create(
        template=template, options=["Open", "Closed"]
    )
    record1 = test_helpers.create_data_sheet(template=template, users=[user_1["user"]])
    DataSheetStateEntry.objects.create(
        field=field, record=record1["record"], value="Closed", closed_at=timezone.now()
    )
    record2 = test_helpers.create_data_sheet(template=template, users=[user_1["user"]])
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
