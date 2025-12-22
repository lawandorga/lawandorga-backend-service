from django.db import connection
from pydantic import BaseModel

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

router = Router()


class OutputUsersWithMissingAccess(BaseModel):
    user: int
    records: int
    access: int


@router.get(
    "users_with_missing_access/",
    output_schema=list[OutputUsersWithMissingAccess],
)
def query__users_with_missing_access(statistics_user: StatisticUser):
    return []


class OutputErrorsMonth(BaseModel):
    status: int
    path: str
    count: int


@router.get("errors_month/", output_schema=list[OutputErrorsMonth])
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


class OutputErrorsUser(BaseModel):
    email: str | int
    rlckeys: int
    userkeys: int
    accepted: bool
    locked: bool


@router.get("errors_user/", output_schema=list[OutputErrorsUser])
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


class OutputMigrationStatistic(BaseModel):
    records: float
    records_togo: int
    documents: float
    documents_togo: int


@router.get("migration/", output_schema=OutputMigrationStatistic)
def query__migration_statistic(statistics_user: StatisticUser):
    statement = """
    select * from (
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_datasheet
    union all
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_encryptedrecorddocument
    ) tmp
    """
    data = execute_statement(statement)
    ret = {
        "records": data[0][0],
        "records_togo": data[0][1],
        "documents": data[1][0],
        "documents_togo": data[1][1],
    }
    return ret
