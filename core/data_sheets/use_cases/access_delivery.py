import logging
from uuid import UUID

from core.auth.models import OrgUser
from core.data_sheets.models import DataSheet
from core.folders.domain.aggregates.folder import Folder

# from core.data_sheets.use_cases.record import migrate_record_into_folder
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.models import Permission
from core.permissions.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from core.seedwork.use_case_layer import use_case

logger = logging.getLogger("django")


@use_case
def deliver_access_to_users_who_should_have_access(
    __actor: OrgUser, r: FolderRepository
):
    records_1 = DataSheet.objects.filter(
        template__rlc_id=__actor.org_id
    ).select_related("template")
    records_2 = list(records_1)

    permission = Permission.objects.get(name=PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    users_1 = OrgUser.objects.filter(org_id=__actor.org_id)
    users_2 = list(users_1)
    users_3 = [u for u in users_2 if u.has_permission(permission)]

    folders: dict[UUID, Folder] = r.get_dict(__actor.org_id)
    changed_folders: set[Folder] = set()
    for record in records_2:
        if not record.has_access(__actor):
            continue

        for user in users_3:
            if record.has_access(user):
                continue

            assert record.folder_uuid is not None
            folder = folders[record.folder_uuid]
            if folder.has_access(user):
                continue
            folder.grant_access(user, __actor)
            changed_folders.add(folder)
            logger.info(f"User {user.uuid} was given access to {record.uuid}")

    for folder in changed_folders:
        r.save(folder)
