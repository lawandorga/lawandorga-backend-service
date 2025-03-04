import io
import json
import sys

import pytest
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import Client

from core.auth.models import OrgUser
from core.data_sheets.models import (
    DataSheetEncryptedFileEntry,
    DataSheetEncryptedFileField,
    DataSheetTemplate,
)
from core.data_sheets.models.data_sheet import (
    DataSheetEncryptedSelectEntry,
    DataSheetEncryptedStandardEntry,
    DataSheetMultipleEntry,
    DataSheetSelectEntry,
    DataSheetStandardEntry,
    DataSheetStateEntry,
    DataSheetStatisticEntry,
    DataSheetUsersEntry,
)
from core.data_sheets.models.template import (
    DataSheetEncryptedSelectField,
    DataSheetEncryptedStandardField,
    DataSheetMultipleField,
    DataSheetSelectField,
    DataSheetStandardField,
    DataSheetStateField,
    DataSheetStatisticField,
    DataSheetUsersField,
)
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.models import UserProfile
from core.org.models.org import Org
from core.permissions.models import HasPermission, Permission
from core.permissions.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES,
    PERMISSION_RECORDS_ADD_RECORD,
)
from core.seedwork import test_helpers


def get_file(text: str = "test-file-text"):
    file = io.BytesIO(bytes(text, "utf-8"))
    mem_file = InMemoryUploadedFile(
        file, "FileField", "test.txt", "text/plain", sys.getsizeof(file), None
    )
    return mem_file


@pytest.fixture
def setup():
    rlc = Org.objects.create(name="Test RLC")
    user = UserProfile.objects.create(email="dummy@law-orga.de", name="Dummy 1")
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    rlc_user = OrgUser(user=user, email_confirmed=True, accepted=True, org=rlc)
    rlc_user.generate_keys(settings.DUMMY_USER_PASSWORD)
    rlc_user.save()
    template = DataSheetTemplate.objects.create(rlc=rlc, name="Record Template")
    permission = Permission.objects.get(name=PERMISSION_RECORDS_ADD_RECORD)
    HasPermission.objects.create(user=user.rlc_user, permission=permission)
    permission = Permission.objects.get(name=PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    HasPermission.objects.create(user=rlc_user, permission=permission)
    template = DataSheetTemplate.objects.create(rlc=rlc, name="Record Template")
    record = test_helpers.create_data_sheet(template, [user])["record"]
    aes_key_record = record.get_aes_key(user.rlc_user)
    yield {
        "login": {"email": user.email, "password": settings.DUMMY_USER_PASSWORD},
        "record": record,
        "template": template,
        "aes_key_record": aes_key_record,
    }


@pytest.fixture
def login(setup):
    yield setup["login"]


@pytest.fixture
def auth_client(login):
    client = Client()
    client.login(**login)
    yield client


@pytest.fixture
def record(setup):
    yield setup["record"]


@pytest.fixture
def template(setup):
    yield setup["template"]


@pytest.fixture
def file_field(setup):
    field = DataSheetEncryptedFileField.objects.create(template=setup["template"])
    yield field


@pytest.fixture
def aes_key_record(setup):
    yield setup["aes_key_record"]


@pytest.fixture
def file_entry(setup, file_field):
    entry = DataSheetEncryptedFileEntry.objects.create(
        record=setup["record"], field=file_field
    )
    file = entry.encrypt_file(
        get_file(), record=setup["record"], aes_key_record=setup["aes_key_record"]
    )
    entry.save()
    entry.file.save("test.txt", file)
    yield entry
    entry.file.delete()
    entry.delete()


@pytest.fixture
def post(auth_client):
    return lambda d: auth_client.post("/api/command/", d)


def test_file_entry_create(db, setup, file_field):
    client = Client()
    client.login(**setup["login"])
    record = setup["record"]
    aes_key_record = setup["aes_key_record"]
    field = file_field

    data = {
        "record_id": record.pk,
        "field_id": field.uuid,
        "file": get_file("test-string"),
    }
    response = client.post("/api/command/?action=data_sheets/create_file_entry", data)
    assert response.status_code == 200
    assert DataSheetEncryptedFileEntry.objects.count() == 1
    entry = DataSheetEncryptedFileEntry.objects.get()
    assert entry.file.read() != "test-string"
    entry.file.seek(0)
    file = entry.decrypt_file(aes_key_record=aes_key_record)
    assert b"test-string" == file.read()
    # clean up the after the tests
    entry.file.delete()
    entry.delete()


def test_file_entry_delete(db, setup, file_field, file_entry):
    client = Client()
    client.login(**setup["login"])
    record = setup["record"]
    data = {
        "record_id": record.pk,
        "field_id": file_field.uuid,
        "action": "data_sheets/delete_entry",
    }
    assert DataSheetEncryptedFileEntry.objects.count() == 1
    response = client.post("/api/command/", data)
    assert response.status_code == 200
    assert DataSheetEncryptedFileEntry.objects.count() == 0


@pytest.fixture
def standard_field(template):
    field = DataSheetStandardField.objects.create(template=template)
    yield field


@pytest.fixture
def standard_entry(standard_field, record):
    entry = DataSheetStandardEntry.objects.create(
        record=record, field=standard_field, value="test text"
    )
    yield entry


def test_standard_entry_create(db, standard_field, record, auth_client):
    data = {
        "record_id": record.pk,
        "field_id": standard_field.uuid,
        "value": "Hallo",
        "action": "data_sheets/create_or_update_entry",
    }
    response = auth_client.post("/api/command/", data)
    assert response.status_code == 200
    assert DataSheetStandardEntry.objects.count() == 1
    assert DataSheetStandardEntry.objects.get().value == "Hallo"


def test_standard_entry_update(db, standard_entry, post):
    data = {
        "value": "Hallo 2",
        "action": "data_sheets/create_or_update_entry",
        "record_id": standard_entry.record.pk,
        "field_id": standard_entry.field.uuid,
    }
    assert DataSheetStandardEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    entry = DataSheetStandardEntry.objects.get()
    assert entry.value == "Hallo 2"


def test_standard_entry_delete(db, standard_entry, post):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": standard_entry.record.id,
        "field_id": standard_entry.field.uuid,
    }
    response = post(data)
    assert response.status_code == 200
    assert DataSheetStandardEntry.objects.count() == 0


@pytest.fixture
def select_field(db, template):
    field = DataSheetSelectField.objects.create(
        template=template, options=["Option 1", "Option 2"]
    )
    yield field


@pytest.fixture
def select_entry(db, select_field, record):
    entry = DataSheetSelectEntry.objects.create(
        record=record, field=select_field, value="Option 1"
    )
    yield entry


def test_select_entry_create(db, record, select_field, post):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": select_field.uuid,
        "value": "Option 1",
    }
    response = post(data)
    assert response.status_code == 200
    assert DataSheetSelectEntry.objects.count() == 1
    entry = DataSheetSelectEntry.objects.get()
    assert entry.value == "Option 1"


def test_select_entry_update(db, record, select_field, post, select_entry):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": select_field.uuid,
        "value": "Option 2",
    }
    assert DataSheetSelectEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    entry = DataSheetSelectEntry.objects.get()
    assert entry.value == "Option 2"


def test_select_entry_delete(db, record, select_field, post, select_entry):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": select_field.uuid,
    }
    assert DataSheetSelectEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    assert DataSheetSelectEntry.objects.count() == 0


def test_select_entry_create_value_in_options(db, record, select_field, post):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": select_field.uuid,
        "value": "Option 3",
    }
    response = post(data)
    assert response.status_code == 400
    assert DataSheetSelectEntry.objects.count() == 0


def test_select_entry_update_value_in_options(
    db, record, select_field, post, select_entry
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": select_field.uuid,
        "value": "Option 3",
    }
    assert DataSheetSelectEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 400
    entry = DataSheetSelectEntry.objects.get()
    assert entry.value == "Option 1"


@pytest.fixture
def state_field(template):
    field = DataSheetStateField.objects.create(
        template=template, options=["Closed", "Option 2"]
    )
    yield field


@pytest.fixture
def state_entry(state_field, record):
    entry = DataSheetStateEntry.objects.create(
        record=record, field=state_field, value="Option 1"
    )
    yield entry


def test_state_entry_create(db, record, state_field, post):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": state_field.uuid,
        "value": "Option 2",
    }
    response = post(data)
    assert response.status_code == 200
    assert DataSheetStateEntry.objects.count() == 1
    entry = DataSheetStateEntry.objects.get()
    assert entry.value == "Option 2"


def test_state_entry_update(db, record, state_field, post, state_entry):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": state_field.uuid,
        "value": "Option 2",
    }
    assert DataSheetStateEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    entry = DataSheetStateEntry.objects.get()
    assert entry.value == "Option 2"


def test_state_entry_delete(db, record, state_field, post, state_entry):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": state_field.uuid,
    }
    assert DataSheetStateEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    assert DataSheetStateEntry.objects.count() == 0


def test_state_entry_create_value_in_options(db, record, state_field, post):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": state_field.uuid,
        "value": "Option 3",
    }
    response = post(data)
    assert response.status_code == 400
    assert DataSheetStateEntry.objects.count() == 0


def test_state_entry_create_value_empty(db, record, state_field, post):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": state_field.uuid,
        "value": "",
    }
    response = post(data)
    assert response.status_code == 400
    assert DataSheetStateEntry.objects.count() == 0


def test_state_entry_update_value_in_options(
    db, record, state_field, post, state_entry
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": state_field.uuid,
        "value": "Option 3",
    }
    assert DataSheetStateEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 400
    entry = DataSheetStateEntry.objects.get()
    assert entry.value == "Option 1"


@pytest.fixture
def multiple_field(template):
    field = DataSheetMultipleField.objects.create(
        template=template, options=["Option 1", "Option 2"]
    )
    yield field


@pytest.fixture
def multiple_entry(multiple_field, record):
    entry = DataSheetMultipleEntry.objects.create(
        record=record, field=multiple_field, value=["Option 1", "Option 2"]
    )
    yield entry


def test_multiple_entry_create(db, record, multiple_field, auth_client):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(multiple_field.uuid),
        "value": ["Option 1"],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    assert DataSheetMultipleEntry.objects.count() == 1
    entry = DataSheetMultipleEntry.objects.get()
    assert entry.value == ["Option 1"]


def test_multiple_entry_update(db, record, multiple_field, auth_client, multiple_entry):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(multiple_field.uuid),
        "value": ["Option 2"],
    }
    assert DataSheetMultipleEntry.objects.count() == 1
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    entry = DataSheetMultipleEntry.objects.get()
    assert entry.value == ["Option 2"]


def test_multiple_entry_delete(db, record, multiple_field, auth_client, multiple_entry):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": str(multiple_field.uuid),
    }
    assert DataSheetMultipleEntry.objects.count() == 1
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    assert DataSheetMultipleEntry.objects.count() == 0


def test_multiple_entry_create_values_must_be_in_options(
    db, record, multiple_field, auth_client
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(multiple_field.uuid),
        "value": ["Option 2", "Option 3"],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 400
    assert DataSheetMultipleEntry.objects.count() == 0


def test_multiple_entry_update_values_must_be_in_options(
    db, record, multiple_field, auth_client, multiple_entry
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(multiple_field.uuid),
        "value": ["Option 2", "Option 3"],
    }
    assert DataSheetMultipleEntry.objects.count() == 1
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 400
    entry = DataSheetMultipleEntry.objects.get()
    assert entry.value == ["Option 1", "Option 2"]


@pytest.fixture
def statistic_field(template):
    field = DataSheetStatisticField.objects.create(
        template=template, options=["Option 1", "Option 2"]
    )
    yield field


@pytest.fixture
def statistic_entry(statistic_field, record):
    entry = DataSheetStatisticEntry.objects.create(
        record=record, field=statistic_field, value="Option 1"
    )
    yield entry


def test_statistic_entry_create(db, record, statistic_field, post):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": statistic_field.uuid,
        "value": "Option 1",
    }
    response = post(data)
    assert response.status_code == 200
    assert DataSheetStatisticEntry.objects.count() == 1
    entry = DataSheetStatisticEntry.objects.get()
    assert entry.value == "Option 1"


def test_statistic_entry_update(db, record, statistic_field, post, statistic_entry):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": statistic_field.uuid,
        "value": "Option 2",
    }
    assert DataSheetStatisticEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    entry = DataSheetStatisticEntry.objects.get()
    assert entry.value == "Option 2"


def test_statistic_entry_delete(db, record, statistic_field, post, statistic_entry):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": statistic_field.uuid,
    }
    assert DataSheetStatisticEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    assert DataSheetStatisticEntry.objects.count() == 0


@pytest.fixture
def users_field(template):
    field = DataSheetUsersField.objects.create(template=template)
    yield field


@pytest.fixture
def users_entry(users_field, record):
    entry = DataSheetUsersEntry.objects.create(record=record, field=users_field)
    yield entry


def test_users_entry_create(db, record, users_field, auth_client):
    user = OrgUser.objects.get()
    user1 = test_helpers.create_org_user(
        rlc=user.org, email="dummy2@law-orga.de", save=True
    )["rlc_user"]
    user2 = test_helpers.create_org_user(
        rlc=user.org, email="dummy3@law-orga.de", save=True
    )["rlc_user"]
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
        "value": [str(user1.pk), str(user2.pk)],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    assert DataSheetUsersEntry.objects.count() == 1
    entry = DataSheetUsersEntry.objects.get()
    assert entry.value.all().count() == 2


def test_users_entry_udpate(db, record, users_field, auth_client, users_entry):
    user = OrgUser.objects.get()
    user2 = test_helpers.create_org_user(
        rlc=user.org, email="dummy3@law-orga.de", save=True
    )["rlc_user"]
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
        "value": [str(user2.pk)],
    }
    assert DataSheetUsersEntry.objects.count() == 1
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    entry = DataSheetUsersEntry.objects.get()
    assert entry.value.all().count() == 1


def test_entry_delete(db, record, users_field, auth_client, users_entry):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
    }
    assert DataSheetUsersEntry.objects.count() == 1
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    assert DataSheetUsersEntry.objects.count() == 0


def test_entry_keys_sharing_true(db, record, users_field, auth_client):
    assert users_field.share_keys is True
    user = OrgUser.objects.get()
    user1 = test_helpers.create_org_user(
        rlc=user.org, email="dummy2@law-orga.de", save=True
    )["rlc_user"]
    user2 = test_helpers.create_org_user(
        rlc=user.org, email="dummy3@law-orga.de", save=True
    )["rlc_user"]
    r = DjangoFolderRepository()
    folder1 = r.retrieve(user.org_id, record.folder_uuid)
    assert folder1.has_access(user2) is False
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
        "value": [str(user2.pk)],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    folder2 = r.retrieve(user.org_id, record.folder_uuid)
    assert folder2.has_access(user2) is True

    # update
    assert folder2.has_access(user1) is False
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
        "value": [str(user1.pk)],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    folder3 = r.retrieve(user.org_id, record.folder_uuid)
    assert folder3.has_access(user1) is True


def test_entry_keys_sharing_false(db, record, users_field, auth_client):
    users_field.share_keys = False
    users_field.save()
    assert users_field.share_keys is False
    user = OrgUser.objects.get()
    user1 = test_helpers.create_org_user(
        rlc=user.org, email="dummy2@law-orga.de", save=True
    )["rlc_user"]
    user2 = test_helpers.create_org_user(
        rlc=user.org, email="dummy3@law-orga.de", save=True
    )["rlc_user"]
    r = DjangoFolderRepository()
    folder1 = r.retrieve(user.org_id, record.folder_uuid)
    assert folder1.has_access(user2) is False
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
        "value": [str(user2.pk)],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    folder2 = r.retrieve(user.org_id, record.folder_uuid)
    assert folder2.has_access(user2) is False

    # update
    assert folder2.has_access(user1) is False
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(users_field.uuid),
        "value": [str(user1.pk)],
    }
    response = auth_client.post(
        "/api/command/", json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    folder3 = r.retrieve(user.org_id, record.folder_uuid)
    assert folder3.has_access(user1) is False


@pytest.fixture
def enc_standard_field(template):
    field = DataSheetEncryptedStandardField.objects.create(template=template)
    yield field


@pytest.fixture
def enc_standard_entry(enc_standard_field, record):
    entry = DataSheetEncryptedStandardEntry.objects.create(
        record=record, field=enc_standard_field, value=b""
    )
    yield entry


def test_enc_standard_entry_create(
    db, record, enc_standard_field, post, aes_key_record
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": enc_standard_field.uuid,
        "value": "Hallo",
    }
    response = post(data)
    assert response.status_code == 200
    assert DataSheetEncryptedStandardEntry.objects.count() == 1
    entry = DataSheetEncryptedStandardEntry.objects.get()
    assert entry.value != b"Hallo" and entry.value != "Hallo"
    entry.decrypt(aes_key_record=aes_key_record)
    assert entry.value == "Hallo"


def test_enc_standard_entry_update(
    db, record, enc_standard_field, post, enc_standard_entry, aes_key_record
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": enc_standard_field.uuid,
        "value": "Hallo 2",
    }
    assert DataSheetEncryptedStandardEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    entry = DataSheetEncryptedStandardEntry.objects.get()
    assert entry.value != b"Hallo 2" and entry.value != "Hallo 2"
    entry.decrypt(aes_key_record=aes_key_record)
    assert entry.value == "Hallo 2"


def test_enc_standard_entry_delete(
    db, record, enc_standard_field, post, enc_standard_entry
):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": enc_standard_field.uuid,
    }
    assert DataSheetEncryptedStandardEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    assert DataSheetEncryptedStandardEntry.objects.count() == 0


@pytest.fixture
def enc_select_field(template):
    field = DataSheetEncryptedSelectField.objects.create(
        template=template, options=["Option 1", "Option 2"]
    )
    yield field


@pytest.fixture
def enc_select_entry(enc_select_field, record, aes_key_record):
    entry = DataSheetEncryptedSelectEntry(
        record=record, field=enc_select_field, value="Option 1"
    )
    entry.encrypt(aes_key_record=aes_key_record)
    entry.save()
    yield entry


def test_enc_select_entry_create(db, record, enc_select_field, post, aes_key_record):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": enc_select_field.uuid,
        "value": "Option 1",
    }
    response = post(data)
    assert response.status_code == 200
    assert DataSheetEncryptedSelectEntry.objects.count() == 1
    entry = DataSheetEncryptedSelectEntry.objects.get()
    assert entry.value != "Option 1" and entry.value != b"Option 1"
    entry.decrypt(aes_key_record=aes_key_record)
    assert entry.value == "Option 1"


def test_enc_select_entry_update(
    db, record, enc_select_field, post, enc_select_entry, aes_key_record
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": enc_select_field.uuid,
        "value": "Option 2",
    }
    assert DataSheetEncryptedSelectEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    entry = DataSheetEncryptedSelectEntry.objects.get()
    assert entry.value != "Option 2" and entry.value != b"Option 2"
    entry.decrypt(aes_key_record=aes_key_record)
    assert entry.value == "Option 2"


def test_enc_select_entry_delete(db, record, enc_select_field, post, enc_select_entry):
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": enc_select_field.uuid,
    }
    assert DataSheetEncryptedSelectEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 200
    assert DataSheetEncryptedSelectEntry.objects.count() == 0


def test_enc_select_entry_create_value_in_options(
    db, record, enc_select_field, post, aes_key_record
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": enc_select_field.uuid,
        "value": "Option 3",
    }
    response = post(data)
    assert response.status_code == 400
    assert DataSheetEncryptedSelectEntry.objects.count() == 0


def test_enc_select_entry_update_value_in_options(
    db, record, enc_select_field, post, enc_select_entry, aes_key_record
):
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": enc_select_field.uuid,
        "value": "Option 3",
    }
    assert DataSheetEncryptedSelectEntry.objects.count() == 1
    response = post(data)
    assert response.status_code == 400
    entry = DataSheetEncryptedSelectEntry.objects.get()
    entry.decrypt(aes_key_record=aes_key_record)
    assert entry.value == "Option 1"


def test_file_entry_download(db, auth_client, file_entry):
    response = auth_client.get(
        "/api/data_sheets/query/file_entry_download/{}/{}/".format(
            file_entry.record.pk, file_entry.field.uuid
        )
    )
    assert response.status_code == 200
    assert b"test-file-text" in response.getvalue()


def test_record_updated_is_updated_on_create(db, post, standard_field, record):
    updated = record.updated
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(standard_field.uuid),
        "value": "Hallo",
    }
    response = post(data)
    assert response.status_code == 200
    record.refresh_from_db()
    assert record.updated > updated


def test_record_updated_on_update(db, post, standard_field, standard_entry, record):
    updated = record.updated
    data = {
        "action": "data_sheets/create_or_update_entry",
        "record_id": record.pk,
        "field_id": str(standard_field.uuid),
        "value": "Hallo",
    }
    response = post(data)
    assert response.status_code == 200
    record.refresh_from_db()
    assert record.updated > updated


def test_record_updated_on_delete(db, post, standard_field, standard_entry, record):
    updated = record.updated
    data = {
        "action": "data_sheets/delete_entry",
        "record_id": record.pk,
        "field_id": str(standard_field.uuid),
    }
    response = post(data)
    assert response.status_code == 200
    record.refresh_from_db()
    assert record.updated > updated
