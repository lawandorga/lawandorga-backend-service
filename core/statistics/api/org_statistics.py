from django.db import connection
from pydantic import BaseModel

from core.auth.models import OrgUser, StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from core.statistics.api.utils import get_available_datasheet_years

from . import schemas
from seedwork.functional import list_filter, list_map

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


@router.get(url="org_members/", output_schema=list[schemas.OutputOrgMembers])
def query__org_members(statistics_user: StatisticUser):
    statement = """
            select
                core_org.name as org_name,
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
        org.name as name,
        count(distinct record.id) as records,
        count(distinct file.id) as files,
        count(distinct collab.id) as collabs
    from core_org as org
    left join core_datasheettemplate template on org.id = template.org_id
    left join core_datasheet record on record.template_id = template.id
    left join core_folder folder on org.id = folder.org_id
    left join core_file file on file.folder_id = folder.id
    left join core_collab collab on org.id = collab.org_id
    group by org.id, org.name;
    """
    data = execute_statement(statement)
    data = list(
        map(
            lambda x: {"lc": x[0], "records": x[1], "files": x[2], "documents": x[3]},
            data,
        )
    )
    return data


class OutputCreatedClosedStats(BaseModel):
    month: str
    created: int
    closed: int


class OutputRecordsCreatedClosed(BaseModel):
    years: list[int]
    data: list[OutputCreatedClosedStats]


class InputCreatedAndClosed(BaseModel):
    year: str | None = None


@router.api(
    url="records_created_and_closed/",
    output_schema=OutputRecordsCreatedClosed,
)
def get_records_created_and_closed(org_user: OrgUser, data: InputCreatedAndClosed):
    if connection.vendor == "sqlite":
        statement = """
        select t1.month as month, t2.month as month, created, closed
        from (
        select strftime('%Y/%m', r.created) as month, count(*) as created
        from core_datasheet r
        left join core_datasheettemplate t on t.id = r.template_id
        where t.org_id = {}
        group by strftime('%Y/%m', r.created), t.org_id
        ) t1
        left outer join (
        select strftime('%Y/%m', se.closed_at) as month, count(*) as closed
        from core_datasheetstateentry se
        left join core_datasheet r on se.record_id = r.id
        left join core_datasheettemplate t on t.id = r.template_id
        where se.value = 'Closed'
        and t.org_id = {}
        group by strftime('%Y/%m', se.closed_at), t.org_id
        ) t2 on t1.month = t2.month
        order by t1.month
        """.format(
            org_user.org.pk, org_user.org.pk
        )
    else:
        statement = """
        select t1.month as month, t2.month as month, created, closed
        from (
        select to_char(r.created, 'YYYY/MM') as month, count(*) as created
        from core_datasheet r
        left join core_datasheettemplate t on t.id = r.template_id
        where t.org_id = {}
        group by to_char(r.created, 'YYYY/MM'), t.org_id
        ) t1
        full outer join (
        select to_char(se.closed_at, 'YYYY/MM') as month, count(*) as closed
        from core_datasheetstateentry se
        left join core_datasheet r on se.record_id = r.id
        left join core_datasheettemplate t on t.id = r.template_id
        where se.value = 'Closed'
        and t.org_id = {}
        group by to_char(se.closed_at, 'YYYY/MM'), t.org_id
        ) t2 on t1.month = t2.month
        order by t1.month
        """.format(
            org_user.org.pk, org_user.org.pk
        )
    result = execute_statement(statement)
    created_and_closed = list_map(
        result,
        lambda x: {
            "month": str(x[0] or x[1]),
            "created": x[2] or 0,
            "closed": x[3] or 0,
        },
    )
    if data.year:
        created_and_closed = list_filter(
            created_and_closed, lambda x: str(x["month"]).startswith(str(data.year))
        )
    if not created_and_closed:
        return {"years": [], "data": []}

    years = get_available_datasheet_years(org_user.org.pk)
    first_year_str, first_month_str = str(
        min(created_and_closed, key=lambda x: x["month"])["month"]
    ).split("/")
    last_year_str, last_month_str = str(
        max(created_and_closed, key=lambda x: x["month"])["month"]
    ).split("/")

    first_year, first_month = int(first_year_str), int(first_month_str)
    last_year, last_month = int(last_year_str), int(last_month_str)
    existing_map = {item["month"]: item for item in created_and_closed}
    current_year, current_month = int(first_year), int(first_month)
    created_and_closed_continuous = []

    while (current_year < last_year) or (
        current_year == last_year and current_month <= last_month
    ):
        month_str = f"{current_year:04d}/{current_month:02d}"
        if month_str in existing_map:
            created_and_closed_continuous.append(existing_map[month_str])
        else:
            created_and_closed_continuous.append(
                {
                    "month": month_str,
                    "created": 0,
                    "closed": 0,
                }
            )
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    return {"years": list(years), "data": created_and_closed_continuous}
