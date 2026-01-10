from django.db import transaction

from core.auth.models.org_user import OrgUser
from core.auth.use_cases.finders import org_user_from_id
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.org.models.org_encryption import OrgEncryption
from core.seedwork.use_case_layer.layer import use_case
from messagebus.domain.collector import EventCollector


@use_case
def optimize(__actor: OrgUser):
    users = list(__actor.org.users.exclude(pk=__actor.pk))

    # fix keyrings of other users
    for user in users:
        if not hasattr(user, "keyring"):
            continue
        if user.keyring.has_invalid_keys:
            user.keyring.fix_self(__actor.keyring)
            user.keyring.store()

    # fix folder keys of other users
    r = DjangoFolderRepository()
    folders = r.get_list(__actor.org_id)
    for f in folders:
        if f.has_access(__actor):
            for u in users:
                if not hasattr(u, "keyring"):
                    continue
                if f.has_invalid_keys(u):
                    f.fix_keys(u, __actor)
                    r.save(f)


@use_case
def fix_keys(__actor: OrgUser, of_pk: int):
    of = org_user_from_id(__actor, of_pk)

    # fix the org key which can be removed once files are migrated to folders
    aes_key_rlc = __actor.org.get_aes_key(
        user=__actor.user, private_key_user=__actor.keyring.get_private_key()
    )
    new_keys = OrgEncryption(user=of.user, rlc=of.org, encrypted_key=aes_key_rlc)

    of.user.users_rlc_keys.all().delete()

    new_keys.encrypt(of.keyring.get_public_key())
    new_keys.save()

    # fix the keyring
    of.keyring.fix_self(__actor.keyring)
    of.keyring.store()


def _test_folder_keys(u: OrgUser):
    r = DjangoFolderRepository()
    folders = r.get_list(u.org_id)

    for folder in folders:
        for key in folder.keys:
            if key.TYPE == "FOLDER" and key.owner_uuid == u.uuid:
                result = key.test(u.keyring)
                if not result:
                    folder.invalidate_keys_of(u)
                    r.save(folder)


@use_case
def check_keys(__actor: OrgUser, collector: EventCollector):
    org_key = __actor.user.users_rlc_keys.get()
    correct = org_key.test(__actor.keyring.get_private_key())
    correct = __actor.keyring.test_keys() and correct
    if not correct:
        with transaction.atomic():
            __actor.lock(collector)
            org_key.save()
            __actor.save()
            __actor.keyring.store()
    _test_folder_keys(__actor)


USECASES = {"encryption/optimize": optimize}
