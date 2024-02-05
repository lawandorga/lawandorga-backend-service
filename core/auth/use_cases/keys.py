from core.auth.models.org_user import OrgUser
from core.data_sheets.models.data_sheet import DataSheetEncryptionNew
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def delete_key(__actor: OrgUser, key_id: int):
    key = DataSheetEncryptionNew.objects.filter(user=__actor, pk=key_id).first()
    if key is None:
        raise UseCaseError(
            "The key you want to delete does not exist.",
        )
    if key.record.encryptions.filter(correct=True).count() <= 1:
        raise UseCaseError(
            "Not enough people have access to this record. "
            "There needs to be at least one person who must "
            "have access. You can not delete this key.",
        )
    if key.correct:
        raise UseCaseError("You can not delete a key that works.")
    key.delete()


@use_case
def check_keys(__actor: OrgUser):
    private_key_user = __actor.get_private_key()
    __actor.user.test_all_keys(private_key_user)
    __test_folder_keys(__actor)
    __test_group_keys(__actor)


def __test_folder_keys(u: OrgUser):
    r = DjangoFolderRepository()
    folders = r.get_list(u.org_id)

    for folder in folders:
        for key in folder.keys:
            if key.TYPE == "FOLDER" and key.owner_uuid == u.uuid:
                result = key.test(u)
                if not result:
                    folder.invalidate_keys_of(u)
                    r.save(folder)


def __test_group_keys(u: OrgUser):
    for g in u.get_groups():
        key = g.get_enc_group_key_of_user(u)
        if key is not None:
            result = key.test(u)
            if not result:
                g.invalidate_keys_of(u)
                g.save()
