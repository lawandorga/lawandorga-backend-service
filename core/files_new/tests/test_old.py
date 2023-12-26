# import pytest

# from core.auth.models.org_user import OrgUser
# from core.data_sheets.models import DataSheet, DataSheetEncryptionNew, DataSheetTemplate
# from core.data_sheets.use_cases.access_delivery import (
#     deliver_access_to_users_who_should_have_access,
# )
# from core.files_new.models import EncryptedRecordDocument
# from core.seedwork.encryption import AESEncryption
# from core.seedwork.use_case_layer import use_case


# @use_case
# def disable_put_files_inside_of_folders(__actor: OrgUser):
#     files1 = (
#         EncryptedRecordDocument.objects.filter(folder_uuid=None)
#         .filter(org=__actor.org)
#         .exclude(record=None)
#         .select_related("record")
#     )
#     files2: list[EncryptedRecordDocument] = list(files1)
#     for file in files2:
#         if file.record:
#             record = file.record
#             if record.folder_uuid:
#                 folder = record.folder.folder
#                 file.key = file.record.key
#                 file.folder.put_obj_in_folder(folder)
#                 file.save()


# def disable_test_put_inside_folders(db, user):
#     user.user.save()
#     user.org.save()
#     user.save()
#     template = DataSheetTemplate.objects.create(name="test", rlc=user.org)
#     record = DataSheet.objects.create(template=template)
#     key = AESEncryption.generate_secure_key()
#     enc = DataSheetEncryptionNew(record=record, user=user, key=key)
#     enc.encrypt(user.get_public_key())
#     enc.save()
#     file = EncryptedRecordDocument.objects.create(
#         name="test.txt", record=record, org=user.org, location="test"
#     )
#     assert file.folder_uuid is None and record.folder_uuid is None
#     deliver_access_to_users_who_should_have_access(user)
#     record = DataSheet.objects.get(pk=record.pk)
#     file = EncryptedRecordDocument.objects.get(pk=file.pk)
#     assert record.folder_uuid is not None and file.folder_uuid is None
#     disable_put_files_inside_of_folders(user)
#     record = DataSheet.objects.get(pk=record.pk)
#     file = EncryptedRecordDocument.objects.get(pk=file.pk)
#     assert record.folder_uuid is not None and file.folder_uuid is not None
#     assert file.folder.has_access(user)
#     assert file.folder.folder == record.folder.folder
