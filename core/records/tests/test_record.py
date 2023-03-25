import json

from django.test import Client

from core.records.helpers import merge_attrs
from core.seedwork import test_helpers


def test_record_creation(db):
    full_user = test_helpers.create_rlc_user()
    client = Client()
    client.login(**full_user)
    response = client.post(
        "/api/records/v2/records/",
        data=json.dumps({"token": "AZ-001"}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_merge_attrs():
    attrs1 = {"a": 1, "b": 2}
    attrs2 = {"c": 3, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {"a": 1, "b": 2, "c": 3, "d": 4}


def test_merge_attrs_to_list():
    attrs1 = {"a": 1, "b": 2}
    attrs2 = {"a": 3, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {"a": [1, 3], "b": 2, "d": 4}


def test_merge_attrs_to_list_deep():
    attrs1 = {"a": 1, "b": ["a", "b", {"c": 1}]}
    attrs2 = {"a": 3, "b": 4, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {
        "a": [1, 3],
        "b": [["a", "b", {"c": 1}], 4],
        "d": 4,
    }
