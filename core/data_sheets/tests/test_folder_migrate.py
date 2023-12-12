from core.auth.models.org_user import OrgUser
from core.data_sheets.models.data_sheet import (
    DataSheet,
    DataSheetEncryptedStandardEntry,
    DataSheetEncryptionNew,
)
from core.data_sheets.models.template import (
    DataSheetEncryptedStandardField,
    DataSheetTemplate,
)
from core.data_sheets.use_cases.record import migrate_record_into_folder
from core.rlc.models.org import Org
from core.seedwork import test_helpers
from core.seedwork.encryption import AESEncryption


def test_folder_migrate(db):
    full_user = test_helpers.create_org_user()
    user: OrgUser = full_user["rlc_user"]  # type: ignore
    org: Org = full_user["org"]  # type: ignore
    another_full_user = test_helpers.create_org_user(
        email="tester@law-orga.de", name="Mr. Tester", rlc=org
    )
    another_user = another_full_user["rlc_user"]
    template = DataSheetTemplate.objects.create(rlc=org, name="Folder Migrate Test")
    field = DataSheetEncryptedStandardField.objects.create(
        template=template, name="Folder Migrate Test"
    )
    record = DataSheet.objects.create(template=template, name="Folder Migrate Test")
    key = AESEncryption.generate_secure_key()
    enc = DataSheetEncryptionNew(user=user, record=record, key=key)
    enc.encrypt(user.get_public_key())
    enc.save()
    enc = DataSheetEncryptionNew(user=another_user, record=record, key=key)
    enc.encrypt(another_user.get_public_key())
    enc.save()
    SECRET = "FOLDER MIGRATE SHALL SUCCEED"
    entry = DataSheetEncryptedStandardEntry(record=record, field=field, value=SECRET)
    entry.encrypt(aes_key_record=key)
    entry.save()

    migrate_record_into_folder(user, record)

    updated_record = DataSheet.objects.get(uuid=record.uuid)
    assert updated_record.folder_uuid is not None
    same_entry = DataSheetEncryptedStandardEntry.objects.get(pk=entry.pk)
    same_entry.decrypt(
        another_user,
        OrgUser.get_dummy_user_private_key(another_user, "tester@law-orga.de"),
    )
    assert same_entry.value == SECRET
