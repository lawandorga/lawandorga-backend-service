from core.auth.models import RlcUser
from core.records.models import Record
from core.rlc.models import Permission
from core.seedwork.use_case_layer import use_case
from core.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS


@use_case
def deliver_access_to_users_who_should_have_access(__actor: RlcUser):
    records_1 = (
        Record.objects.filter(template__rlc_id=__actor.org_id)
        .select_related("template")
        .prefetch_related("encryptions")
    )
    records_2 = list(records_1)

    permission = Permission.objects.get(name=PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    users_1 = RlcUser.objects.filter(
        permissions__permission=permission, org_id=__actor.org_id
    )
    users_2 = list(users_1)

    for record in records_2:
        if record.has_access(__actor):

            # do this in order to put the record inside a folder
            if not record.folder_uuid:
                record.get_aes_key(__actor)

            for user in users_2:
                if not record.has_access(user):
                    record.grant_access(user, __actor)
