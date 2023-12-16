from django.db import connection

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

from . import schemas

router = Router()


@router.get(
    "users_with_missing_access/",
    output_schema=list[schemas.OutputUsersWithMissingAccess],
)
def query__users_with_missing_access(statistics_user: StatisticUser):
    statement = """
            select u, r, enc
            from (
                     select u.id                   as u,
                            count(distinct r.id)   as r,
                            count(distinct enc.id) as enc

                     from core_userprofile u
                              cross join core_datasheet r

                              left join core_datasheetencryptionnew enc
                                        on enc.user_id = u.id and enc.record_id = r.id

                              left join core_datasheettemplate t on t.id = r.template_id
                              left join core_group_group_members cggm on u.id = cggm.userprofile_id
                              left join core_haspermission ch1 on u.id = ch1.user_has_permission_id
                              left join core_haspermission ch2 on cggm.group_id = ch2.group_has_permission_id
                              left join core_permission cp1 on cp1.id = ch1.permission_id
                              left join core_permission cp2 on cp2.id = ch2.permission_id
                     where (cp1.name = 'records__access_all_records' or cp2.name = 'records__access_all_records')
                       and t.rlc_id = u.rlc_id
                     group by u.id
                 ) t1
            where r<>enc;
            """
    data = execute_statement(statement)
    data = map(lambda x: {"user": x[0], "records": x[1], "access": x[2]}, data)
    return list(data)


@router.get("errors_month/", output_schema=list[schemas.OutputErrorsMonth])
def query__errors_month(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        statement = """
        select status, path, count(*) as count
        from core_loggedpath
        where status > 300
        and status <> 401
        and time > date('now', '-1 month')
        group by status, path
        order by count(*) desc
        limit 20
        """
    else:
        statement = """
        select status, path, count(*) as count
        from core_loggedpath
        where status > 300
        and status <> 401
        and time > current_date - interval '30' day
        group by status, path
        order by count(*) desc
        limit 20
        """
    data = execute_statement(statement)
    data = map(lambda x: {"status": x[0], "path": x[1], "count": x[2]}, data)
    return list(data)


@router.get("errors_user/", output_schema=list[schemas.OutputErrorsUser])
def query__errors_user(statistics_user: StatisticUser):
    statement = """
            select
            baseuser.id,
            rlckeys.id is not null as rlckeys,
            rlcuser.key is not null as userkeys,
            rlcuser.accepted,
            rlcuser.locked
            from core_userprofile baseuser
            inner join core_orguser rlcuser on baseuser.id = rlcuser.user_id
            left join core_orgencryption rlckeys on baseuser.id = rlckeys.user_id
            where rlckeys.id is null or rlcuser.key is null or rlcuser.key = '{}'
            """
    data = execute_statement(statement)
    data = map(
        lambda x: {
            "email": x[0],
            "rlckeys": x[1],
            "userkeys": x[2],
            "accepted": x[3],
            "locked": x[4],
        },
        data,
    )
    return list(data)


@router.get("migration/", output_schema=schemas.OutputMigrationStatistic)
def query__migration_statistic(statistics_user: StatisticUser):
    statement = """
    select * from (
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_datasheet
    union all
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_questionnaire
    union all
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_encryptedrecorddocument
    ) tmp
    """
    data = execute_statement(statement)
    ret = {
        "records": data[0][0],
        "records_togo": data[0][1],
        "questionnaires": data[1][0],
        "questionnaires_togo": data[1][1],
        "documents": data[2][0],
        "documents_togo": data[2][1],
    }
    return ret
