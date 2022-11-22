from django.test import Client


def test_records_page(user, record):
    c = Client()
    c.login(**user)
    response = c.get("/api/records/query/")
    assert response.status_code == 200
