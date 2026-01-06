from core.auth.models.org_user import OrgUser
from core.encryption.models import KeyNotFoundError
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def check_keys(__actor: OrgUser):
    try:
        private_key_user = __actor.keyring.get_private_key()
        __actor.user.users_rlc_keys.get().test(private_key_user)
    except Exception:
        raise UseCaseError("The user key is not correct.")
    try:
        __test_folder_keys(__actor)
    except Exception:
        raise UseCaseError("The folder keys are not correct.")
    try:
        __test_group_keys(__actor)
    except Exception:
        raise UseCaseError("The group keys are not correct.")


def __test_folder_keys(u: OrgUser):
    r = DjangoFolderRepository()
    folders = r.get_list(u.org_id)

    for folder in folders:
        for key in folder.keys:
            if key.TYPE == "FOLDER" and key.owner_uuid == u.uuid:
                result = key.test(u.keyring)
                if not result:
                    folder.invalidate_keys_of(u)
                    r.save(folder)


def __test_group_keys(u: OrgUser):
    for g in u.groups.all():
        try:
            u.keyring.get_group_key(g.uuid)
        except DomainError:
            # key is already invalid
            pass
        except KeyNotFoundError as e:
            # this should never happen
            raise e
        except Exception:
            gkey = u.keyring._find_group_key(g.uuid)
            assert gkey is not None
            gkey.is_invalidated = True
            u.keyring.store()
