from django.test import Client


def test_records_page(user, record):
    c = Client()
    c.login(**user)
    response = c.get("/api/records/query/")
    assert response.status_code == 200


def test_record_detail(user, record):
    c = Client()
    c.login(**user)
    response = c.get("/api/records/query/{}/".format(record.uuid))
    assert response.status_code == 200
