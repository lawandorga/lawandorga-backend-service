from typing import List

from django.db import connection

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from core.statistics.api import schemas
from core.statistics.api.schemas import (
    OutputRecordClosedStatistic,
    OutputRecordFieldAmount,
)
from core.statistics.use_cases.records import create_statistic

router = Router()


@router.api(
    url="records_closed_statistic/",
    output_schema=List[OutputRecordClosedStatistic],
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
    return data


# records field amount statistic
@router.api(
    url="record_fields_amount/",
    output_schema=List[OutputRecordFieldAmount],
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
    return data


# build a dynamic statistic
@router.post(
    url="dynamic/",
    output_schema=schemas.OutputRecordStats,
)
def get_dynamic_record_stats(
    data: schemas.InputRecordStats, statistics_user: StatisticUser
):
    ret = create_statistic(statistics_user, data.field_1, data.value_1, data.field_2)
    return ret
