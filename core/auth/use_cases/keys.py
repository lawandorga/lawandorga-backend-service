from core.auth.models.org_user import OrgUser
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork.use_case_layer import use_case


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
