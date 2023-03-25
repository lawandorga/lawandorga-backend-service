import json
from django.test import Client
from core.seedwork import test_helpers


def test_record_creation(db):
    full_user = test_helpers.create_rlc_user()
    client = Client()
    client.login(**full_user)
    response = client.post("/api/records/v2/records/", data=json.dumps({"token": "AZ-001"}), content_type='application/json')
    assert response.status_code == 200
