from typing import List

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from core.statistics.api.schemas import OutputUserWithMissingRecordKeys

router = Router()


# list keys
@router.api(
    url="users_with_missing_record_keys/",
    output_schema=List[OutputUserWithMissingRecordKeys],
)
def get_users_with_missing_record_keys(statistics_user: StatisticUser):
    statement = """
           select u, r, enc
           from (
                    select u.id                   as u,
                           count(distinct r.id)   as r,
                           count(distinct enc.id) as enc

                    from core_userprofile u
                             cross join core_record r

                             left join core_recordencryptionnew enc
                                       on enc.user_id = u.id and enc.record_id = r.id
                             left join core_rlcuser ru on ru.user_id = u.id
                             left join core_recordtemplate t on t.id = r.template_id
                             left join core_group_members cggm on ru.id = cggm.rlcuser_id
                             left join core_haspermission ch1 on ru.id = ch1.user_id
                             left join core_haspermission ch2 on cggm.group_id = ch2.group_has_permission_id
                             left join core_permission cp1 on cp1.id = ch1.permission_id
                             left join core_permission cp2 on cp2.id = ch2.permission_id
                    where (cp1.name = 'records__access_all_records' or cp2.name = 'records__access_all_records')
                    and t.rlc_id = ru.org_id
                    group by u.id
                ) t1
           where r<>enc;
           """
    data = execute_statement(statement)
    data = list(map(lambda x: {"user": x[0], "records": x[1], "access": x[2]}, data))
    return data
