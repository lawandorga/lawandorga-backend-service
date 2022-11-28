from typing import cast

from django.db import transaction

from core.auth.models import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_id
from core.records.models import Record, RecordUpgrade
from core.records.use_cases.finders import template_from_id
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, find, use_case
from core.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_record(
    __actor: RlcUser, folder=find(folder_from_id), template=find(template_from_id)
):
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    for user in list(__actor.org.users.all()):
        if user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS):
            folder.grant_access(user, __actor)

    record = Record(template=template)

    upgrade = None
    for u in folder.upgrades:
        if isinstance(u, RecordUpgrade):
            upgrade = u
            break
    if upgrade is None:
        upgrade = RecordUpgrade(raw_folder_id=folder.pk)
        folder.add_upgrade(upgrade)

    record.upgrade = upgrade
    record.generate_key(__actor)

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))

    with transaction.atomic():
        upgrade.save()
        r.save(folder)
        record.save()

    return record.id
