from typing import cast

from core.auth.models import OrgUser
from core.data_sheets.models import DataSheet
from core.data_sheets.use_cases.record import migrate_record_into_folder
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.models import Permission
from core.permissions.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import use_case


@use_case
def deliver_access_to_users_who_should_have_access(__actor: OrgUser):
    records_1 = (
        DataSheet.objects.filter(template__rlc_id=__actor.org_id)
        .select_related("template")
        .prefetch_related("encryptions")
    )
    records_2 = list(records_1)

    permission = Permission.objects.get(name=PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    users_1 = OrgUser.objects.filter(org_id=__actor.org_id)
    users_2 = list(users_1)
    users_3 = [u for u in users_2 if u.has_permission(permission)]

    for record in records_2:
        if record.has_access(__actor):
            # do this in order to put the record inside a folder
            if not record.folder_uuid:
                migrate_record_into_folder(__actor, record)

            for user in users_3:
                if not record.has_access(user):
                    assert record.folder_uuid is not None
                    r = cast(
                        FolderRepository, RepositoryWarehouse.get(FolderRepository)
                    )
                    folder = r.retrieve(__actor.org_id, record.folder_uuid)
                    folder.grant_access(user, __actor)
                    r.save(folder)
