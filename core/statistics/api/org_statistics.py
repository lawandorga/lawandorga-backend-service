from typing import List

from django.db import connection

from core.auth.models import OrgUser, StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

from . import schemas

router = Router()


@router.get(url="user_actions_month/", output_schema=list[schemas.OutputUserActions])
def query__user_actions(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        statement = """
        select u.id as email, count(*) as actions
        from core_userprofile as u
        left join core_loggedpath path on u.id = path.user_id
        where user_id is not null
        and path.time > date('now', '-1 month')
        group by u.email, u.id
        order by count(*) desc;
        """
    else:
        statement = """
        select u.id as email, count(*) as actions
        from core_userprofile as u
        left join core_loggedpath path on u.id = path.user_id
        where user_id is not null
        and path.time > date_trunc('day', NOW() - interval '1 month')
        group by u.email, u.id
        order by count(*) desc;
        """
    data = execute_statement(statement)
    data = map(lambda x: {"email": x[0], "actions": x[1]}, data)
    return list(data)


@router.get(url="unique_users_month/", output_schema=list[schemas.OutputUniqueUsers])
def query__unique_users(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        statement = """
        select strftime('%Y/%m', time) as month, count(distinct path.user_id) as logins
        from core_loggedpath as path
        group by strftime('%Y/%m', time)
        order by date(time) asc
        """
    else:
        statement = """
        select to_char(time, 'YYYY/MM') as month, count(distinct path.user_id) as logins
        from core_loggedpath as path
        group by to_char(time, 'YYYY/MM')
        order by to_char(time, 'YYYY/MM') asc;
        """
    data = execute_statement(statement)
    data = map(lambda x: {"month": x[0], "logins": x[1]}, data)
    return list(data)


@router.get(url="user_logins_month/", output_schema=list[schemas.OutputUserLoginsMonth])
def query__user_logins_month(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        statement = """
        select strftime('%Y/%m', time) as month, count(*) as logins
        from core_loggedpath as path
        where path.path like '%login%'
        and (path.status = 200 or path.status = 0)
        group by strftime('%Y/%m', time)
        order by date(time) asc;
        """
    else:
        statement = """
        select to_char(time, 'YYYY/MM') as month, count(*) as logins
        from core_loggedpath as path
        where path.path like '%login%'
        and (path.status = 200 or path.status = 0)
        group by to_char(time, 'YYYY/MM')
        order by to_char(time, 'YYYY/MM') asc;
        """
    data = execute_statement(statement)
    data = map(lambda x: {"month": x[0], "logins": x[1]}, data)
    return list(data)


@router.get(url="user_logins/", output_schema=list[schemas.OutputUserLogins])
def query__user_logins(statistics_user: StatisticUser):
    statement = """
            select date(time) as date, count(*) as logins
            from core_loggedpath as path
            where path.path like '%login%'
            and (path.status = 200 or path.status = 0)
            group by date(time)
            order by date(time) asc;
            """
    data = execute_statement(statement)
    data = map(lambda x: {"date": x[0], "logins": x[1]}, data)
    return list(data)


@router.get(url="rlc_members/", output_schema=list[schemas.OutputOrgMembers])
def query__org_members(statistics_user: StatisticUser):
    statement = """
            select
                core_org.name as rlc_name,
                count(distinct core_orguser.id) as member_amount
            from core_orguser
            inner join core_org on core_org.id = core_orguser.org_id
            group by core_orguser.org_id, core_org.name;
            """
    data = execute_statement(statement)
    data = list(map(lambda x: {"name": x[0], "amount": x[1]}, data))
    return data


@router.get(url="lc_usage/", output_schema=list[schemas.OutputOrgUsage])
def query__org_usage(statistics_user: StatisticUser):
    statement = """
    select
        rlc.name as name,
        count(distinct record.id) as records,
        count(distinct file.id) as files,
        count(distinct document.id) as documents
    from core_org as rlc
    left join core_datasheettemplate template on rlc.id = template.rlc_id
    left join core_datasheet record on record.template_id = template.id
    left join core_folder folder on rlc.id = folder.rlc_id
    left join core_file file on file.folder_id = folder.id
    left join core_collabdocument document on rlc.id = document.rlc_id
    group by rlc.id, rlc.name;
    """
    data = execute_statement(statement)
    data = list(
        map(
            lambda x: {"lc": x[0], "records": x[1], "files": x[2], "documents": x[3]},
            data,
        )
    )
    return data


@router.api(
    url="records_created_and_closed/",
    output_schema=List[schemas.OutputRecordsCreatedClosed],
)
def get_records_created_and_closed(org_user: OrgUser):
    if connection.vendor == "sqlite":
        statement = """
        select t1.month as month, t2.month as month, created, closed
        from (
        select strftime('%Y/%m', r.created) as month, count(*) as created
        from core_datasheet r
        left join core_datasheettemplate t on t.id = r.template_id
        where t.rlc_id = {}
        group by strftime('%Y/%m', r.created), t.rlc_id
        ) t1
        left outer join (
        select strftime('%Y/%m', se.closed_at) as month, count(*) as closed
        from core_datasheetstateentry se
        left join core_datasheet r on se.record_id = r.id
        left join core_datasheettemplate t on t.id = r.template_id
        where se.value = 'Closed'
        and t.rlc_id = {}
        group by strftime('%Y/%m', se.closed_at), t.rlc_id
        ) t2 on t1.month = t2.month
        order by t1.month
        """.format(
            org_user.org.id, org_user.org.id
        )
    else:
        statement = """
        select t1.month as month, t2.month as month, created, closed
        from (
        select to_char(r.created, 'YYYY/MM') as month, count(*) as created
        from core_datasheet r
        left join core_datasheettemplate t on t.id = r.template_id
        where t.rlc_id = {}
        group by to_char(r.created, 'YYYY/MM'), t.rlc_id
        ) t1
        full outer join (
        select to_char(se.closed_at, 'YYYY/MM') as month, count(*) as closed
        from core_datasheetstateentry se
        left join core_datasheet r on se.record_id = r.id
        left join core_datasheettemplate t on t.id = r.template_id
        where se.value = 'Closed'
        and t.rlc_id = {}
        group by to_char(se.closed_at, 'YYYY/MM'), t.rlc_id
        ) t2 on t1.month = t2.month
        order by t1.month
        """.format(
            org_user.org.id, org_user.org.id
        )
    data = execute_statement(statement)
    data = list(
        map(
            lambda x: {
                "month": x[0] or x[1],
                "created": x[2] or 0,
                "closed": x[3] or 0,
            },
            data,
        )
    )
    return data
