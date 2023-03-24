from core.auth.models.org_user import RlcUser
from core.data_sheets.models.record import Record, RecordEncryptedStandardEntry, RecordEncryptionNew
from core.data_sheets.models.template import RecordEncryptedStandardField, RecordTemplate
from core.data_sheets.use_cases.record import migrate_record_into_folder
from core.rlc.models.org import Org
from core.seedwork import test_helpers
from core.seedwork.encryption import AESEncryption


def test_folder_migrate(db):
    full_user = test_helpers.create_rlc_user()
    user: RlcUser = full_user["rlc_user"]  # type: ignore
    org: Org = full_user["org"]
    another_full_user = test_helpers.create_rlc_user(email='tester@law-orga.de', name="Mr. Tester", rlc=org)
    another_user = another_full_user["rlc_user"]
    template = RecordTemplate.objects.create(rlc=org, name="Folder Migrate Test")
    field = RecordEncryptedStandardField.objects.create(template=template, name="Folder Migrate Test")
    record = Record.objects.create(template=template, name="Folder Migrate Test")
    key = AESEncryption.generate_secure_key()
    enc = RecordEncryptionNew(user=user, record=record, key=key)
    enc.encrypt(user.get_public_key())
    enc.save()
    enc = RecordEncryptionNew(user=another_user, record=record, key=key)
    enc.encrypt(another_user.get_public_key())
    enc.save()
    SECRET = "FOLDER MIGRATE SHALL SUCCEED"
    entry = RecordEncryptedStandardEntry(record=record, field=field, value=SECRET)
    entry.encrypt(aes_key_record=key)
    entry.save()

    migrate_record_into_folder(user, record)

    updated_record = Record.objects.get(uuid=record.uuid)
    assert updated_record.folder_uuid is not None
    same_entry = RecordEncryptedStandardEntry.objects.get(pk=entry.pk)
    same_entry.decrypt(another_user, RlcUser.get_dummy_user_private_key(another_user, 'tester@law-orga.de'))
    assert same_entry.value == SECRET
