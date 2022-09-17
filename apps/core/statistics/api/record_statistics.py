from typing import List, Optional

from django.db import connection
from pydantic import BaseModel

from apps.core.auth.models import StatisticUser
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

router = Router()


# helpers
def execute_statement(statement):
    cursor = connection.cursor()
    cursor.execute(statement)
    data = cursor.fetchall()
    return data


# schemas
class RecordClosedStatistic(BaseModel):
    days: Optional[int]
    count: int


# records closed statistic
GET_RECORDS_CLOSED_STATISTIC_SUCCESS = (
    "User {} has requested the users with missing record keys."
)


@router.api(
    url="records_closed_statistic/",
    output_schema=List[RecordClosedStatistic],
    auth=True,
)
def get_records_closed_statistic(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        statement = """
            select
            round(julianday(se.closed_at) - julianday(r.created) + 1) as days,
            count(*) as count
            from recordmanagement_record r
            left join recordmanagement_recordstateentry se on r.id = se.record_id
            where se.value = 'Closed'
            group by round(julianday(se.closed_at) - julianday(r.created) + 1)
            order by days;
        """
    else:
        statement = """
            select
            date_part('day', se.closed_at - r.created) + 1 as days,
            count(*)
            from recordmanagement_record r
            left join recordmanagement_recordstateentry se on r.id = se.record_id
            where se.value = 'Closed'
            group by date_part('day', se.closed_at - r.created)
            order by days;
        """
    data = execute_statement(statement)
    data = list(map(lambda x: {"days": x[0], "count": x[1]}, data))
    return ServiceResult(GET_RECORDS_CLOSED_STATISTIC_SUCCESS, data)
