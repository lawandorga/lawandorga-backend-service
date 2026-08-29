import logging
from uuid import UUID

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.models import Permission
from core.permissions.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from core.records.models import RecordsRecord
from core.seedwork.use_case_layer import use_case

logger = logging.getLogger("django")


@use_case
def deliver_access_to_users_who_should_have_access(
    __actor: OrgUser, r: FolderRepository
):
    __actor.keyring.load_with_decryption_key()  # load the keyring to have it in memory for this long running use case
    records_raw = RecordsRecord.objects.filter(org_id=__actor.org_id)
    records = list(records_raw)

    permission = Permission.objects.get(name=PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    users_raw = OrgUser.objects.filter(org_id=__actor.org_id)
    users = list(users_raw)
    users_with_permission = [u for u in users if u.has_permission(permission)]

    folders: dict[UUID, Folder] = r.get_dict(__actor.org_id)
    changed_folders: set[Folder] = set()
    for record in records:
        if not record.has_access(__actor):
            continue

        for user in users_with_permission:
            if record.has_access(user):
                continue

            folder = folders[record.folder_uuid]
            if folder.has_access(user):
                continue

            folder.grant_access(user, __actor)
            changed_folders.add(folder)

            logger.info(f"User {user.uuid} was given access to {record.uuid}")

    for folder in changed_folders:
        r.save(folder)
