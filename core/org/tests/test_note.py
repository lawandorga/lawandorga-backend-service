import pytest
from django.test import Client

from core.models import Note, Org
from core.org.use_cases.note import create_note, delete_note, update_note
from core.permissions.static import PERMISSION_DASHBOARD_MANAGE_NOTES
from core.seedwork import test_helpers


@pytest.fixture
def user(db):
    org = Org.objects.create(name="Test RLC")
    user = test_helpers.create_org_user(org=org)
    user["org_user"].grant(PERMISSION_DASHBOARD_MANAGE_NOTES)
    yield user


@pytest.fixture
def note(db, user):
    note = Note.create(org=user["org_user"].org, title="Test", note="Content", order=1)
    note.save()
    yield note


def test_note_create(db, user):
    create_note(user["org_user"], "Test", "Content", 1)
    assert Note.objects.filter(title="Test").count() == 1


def test_note_update(db, user, note):
    update_note(user["org_user"], note.id, "New", "New")
    assert Note.objects.get(pk=note.pk).title == "New"


def test_note_delete(db, user, note):
    delete_note(user["org_user"], note.id)
    assert Note.objects.filter(pk=note.pk).count() == 0


def test_list_works(db, user, note):
    c = Client()
    c.login(**user)
    response = c.get("/api/notes/")
    assert response.json()
