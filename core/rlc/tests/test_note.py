import json

import pytest
from django.test import Client

from core.models import Note, Org
from core.permissions.static import PERMISSION_DASHBOARD_MANAGE_NOTES
from core.seedwork import test_helpers


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user = test_helpers.create_org_user(rlc=rlc)
    user["rlc_user"].grant(PERMISSION_DASHBOARD_MANAGE_NOTES)
    yield user


@pytest.fixture
def note(db, user):
    note = Note.create(org=user["rlc_user"].org, title="Test", note="Content")
    note.save()
    yield note


def test_note_create(db, user):
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/notes/",
        data=json.dumps({"title": "Test", "note": "Content"}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_note_update(db, user, note):
    c = Client()
    c.login(**user)
    response = c.put(
        "/api/notes/{}/".format(note.id),
        data=json.dumps({"title": "New", "note": "New"}),
        content_type="application/json",
    )
    assert response.status_code == 200 and Note.objects.get(pk=note.pk).title == "New"


def test_note_delete(db, user, note):
    c = Client()
    c.login(**user)
    response = c.delete("/api/notes/{}/".format(note.id))
    assert response.status_code == 200 and Note.objects.filter(pk=note.pk).count() == 0


def test_list_works(db, user, note):
    c = Client()
    c.login(**user)
    response = c.get("/api/notes/")
    assert response.json()
