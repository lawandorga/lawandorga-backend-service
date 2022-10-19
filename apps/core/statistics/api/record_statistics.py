from typing import List, Optional

from django.db import connection
from pydantic import BaseModel

from apps.core.auth.models import StatisticUser
from apps.core.statistics.api import schemas
from apps.core.statistics.use_cases.records import create_statistic
from apps.static.api_layer import PLACEHOLDER, Router
from apps.static.service_layer import ServiceResult
from apps.static.statistics import execute_statement

router = Router()


# records closed statistic
class RecordClosedStatistic(BaseModel):
    days: Optional[int]
    count: int


GET_RECORDS_CLOSED_STATISTIC_SUCCESS = (
    "User {} has requested the users with missing record keys."
)


@router.api(
    url="records_closed_statistic/",
    output_schema=List[RecordClosedStatistic],
)
def get_records_closed_statistic(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        statement = """
            select
            round(julianday(se.closed_at) - julianday(r.created) + 1) as days,
            count(*) as count
            from core_record r
            left join core_recordstateentry se on r.id = se.record_id
            where se.value = 'Closed'
            group by round(julianday(se.closed_at) - julianday(r.created) + 1)
            order by days;
        """
    else:
        statement = """
            select
            date_part('day', se.closed_at - r.created) + 1 as days,
            count(*)
            from core_record r
            left join core_recordstateentry se on r.id = se.record_id
            where se.value = 'Closed'
            group by date_part('day', se.closed_at - r.created)
            order by days;
        """
    data = execute_statement(statement)
    data = list(map(lambda x: {"days": x[0], "count": x[1]}, data))
    return ServiceResult(GET_RECORDS_CLOSED_STATISTIC_SUCCESS, data)


# records field amount statistic
class RecordFieldAmount(BaseModel):
    field: str
    amount: int


GET_RECORDS_FIELD_AMOUNT_STATISTIC = (
    "User {} has requested the count of the record fields."
)


@router.api(
    url="record_fields_amount/",
    output_schema=List[RecordFieldAmount],
)
def get_record_fields_amount(statistics_user: StatisticUser):
    statement = """
    select name, count(*) as amount from (
        select name from core_recordstatefield
        union all
        select name from core_recordstatisticfield
        union all
        select name from core_recordencryptedfilefield
        union all
        select name from core_recordselectfield
        union all
        select name from core_recordencryptedselectfield
        union all
        select name from core_recordstandardfield
        union all
        select name from core_recordusersfield
        union all
        select name from core_recordmultiplefield
        ) t1
    group by name
    order by count(*) desc;
    """
    data = execute_statement(statement)
    data = list(map(lambda x: {"field": x[0], "amount": x[1]}, data))
    return ServiceResult(GET_RECORDS_FIELD_AMOUNT_STATISTIC, data)


# build a dynamic statistic
@router.post(
    url="dynamic/",
    input_schema=schemas.InputRecordStats,
    output_schema=schemas.OutputRecordStats,
)
def get_dynamic_record_stats(
    data: schemas.InputRecordStats, statistics_user: StatisticUser
):
    ret = create_statistic(
        data.field_1, data.value_1, data.field_2, __actor=statistics_user
    )
    return ServiceResult(PLACEHOLDER, ret)
