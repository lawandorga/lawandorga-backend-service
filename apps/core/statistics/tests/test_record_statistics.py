import json

import pytest
from django.test import Client
from django.utils import timezone

from apps.core.fixtures import create_permissions
from apps.core.records.models import RecordStateEntry, RecordStateField, RecordTemplate
from apps.core.rlc.models import Org
from apps.seedwork import test_helpers as data


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_rlc_user(rlc=rlc)
    statistics_user = data.create_statistics_user(
        email="statistics@law-orga.de", name="Mr. Statistics"
    )
    rlc.generate_keys()
    create_permissions()
    template = RecordTemplate.objects.create(rlc=rlc, name="Record Template")
    field = RecordStateField.objects.create(
        template=template, options=["Open", "Closed"]
    )
    record1 = data.create_record(template=template, users=[user_1["user"]])
    RecordStateEntry.objects.create(
        field=field, record=record1["record"], value="Closed", closed_at=timezone.now()
    )
    record2 = data.create_record(template=template, users=[user_1["user"]])
    RecordStateEntry.objects.create(
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
