from django.test import Client


def test_record_detail(user, record):
    c = Client()
    c.login(**user)
    response = c.get("/api/data_sheets/query/{}/".format(record.uuid))
    assert response.status_code == 200
