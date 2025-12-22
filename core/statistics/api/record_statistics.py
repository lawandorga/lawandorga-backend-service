from typing import Any, List, Optional

from django.db import connection
from django.db.models import Count
from django.db.models.functions import ExtractYear
from pydantic import BaseModel

from core.auth.models import StatisticUser
from core.auth.models.org_user import OrgUser
from core.records.models.record import RecordsRecord
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from core.statistics.use_cases.records import create_statistic

router = Router()


class OutputCreatedRecords(BaseModel):
    year: int
    created: int


@router.get(url="created_records/", output_schema=list[OutputCreatedRecords])
def query__created_records(org_user: OrgUser):
    qs = (
        RecordsRecord.objects.filter(org=org_user.org)
        .annotate(year=ExtractYear("created"))
        .values("year")
        .annotate(created=Count("id"))
        .order_by("year")
    )
    return list(qs)


class OutputRecordClientState(BaseModel):
    value: str
    count: int


@router.get(
    url="record_client_state/",
    output_schema=list[OutputRecordClientState],
)
def query__record_client_state(statistics_user: StatisticUser):
    statement = """
           select
           case when entry.value is null then 'Unset' else entry.value end as value,
           count(*) as count
           from core_datasheet record
           left join core_datasheetstatisticentry entry on record.id = entry.record_id
           left join core_datasheetstatisticfield field on entry.field_id = field.id
           where field.name='Current status of the client' or field.name is null
           group by value
           """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


class OutputRecordClientAge(BaseModel):
    value: str
    count: int


@router.get(
    url="record_client_age/",
    output_schema=list[OutputRecordClientAge],
)
def query__record_client_age(statistics_user: StatisticUser):
    statement = """
            select
            case when entry.value is null then 'Unset' else entry.value end as value,
            count(*) as count
            from core_datasheet record
            left join core_datasheetstatisticentry entry on record.id = entry.record_id
            left join core_datasheetstatisticfield field on entry.field_id = field.id
            where field.name='Age in years of the client' or field.name is null
            group by value
            """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


class OutputRecordClientNationality(BaseModel):
    value: str
    count: int


@router.get(
    url="record_client_nationality/",
    output_schema=list[OutputRecordClientNationality],
)
def query__record_client_nationality(statistics_user: StatisticUser):
    statement = """
            select
            case when entry.value is null then 'Unset' else entry.value end as value,
            count(*) as count
            from core_datasheet record
            left join core_datasheetstatisticentry entry on record.id = entry.record_id
            left join core_datasheetstatisticfield field on entry.field_id = field.id
            where field.name='Nationality of the client' or field.name is null
            group by value
            """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


class OutputRecordClientSex(BaseModel):
    value: str
    count: int


@router.get(
    url="record_client_sex/",
    output_schema=list[OutputRecordClientSex],
)
def query__record_client_sex(statistics_user: StatisticUser):
    statement = """
            select
            case when entry.value is null then 'Unset' else entry.value end as value,
            count(*) as count
            from core_datasheet record
            left join core_datasheetstatisticentry entry on record.id = entry.record_id
            left join core_datasheetstatisticfield field on entry.field_id = field.id
            where field.name='Sex of the client' or field.name is null
            group by value
            """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


class OutputRecordStates(BaseModel):
    state: str
    amount: int


@router.get(
    url="record_states/",
    output_schema=list[OutputRecordStates],
)
def query__record_states(statistics_user: StatisticUser):
    statement = """
            select state, count(amount) as amount
            from (
                select count(state.record_id) as amount,
                    state.record_id,
                    case
                        when count(state.record_id) <> 1 or state.value = '' or state.value is null then 'Unknown'
                        else state.value
                    end as state
                from core_datasheet as record
                left join core_datasheetstateentry as state on state.record_id = record.id
                group by record.id, state.record_id, state.value
            ) as tmp
            group by state
            """
    data = execute_statement(statement)
    data = map(lambda x: {"state": x[0], "amount": x[1]}, data)
    return list(data)


class OutputState(BaseModel):
    state: str
    count: int


class OutputTag(BaseModel):
    tag: str
    count: int


class OutputRecordTagStats(BaseModel):
    tags: list[OutputTag]
    state: list[OutputState]
    years: list[int]


@router.get(
    url="tag_stats/",
    output_schema=OutputRecordTagStats,
)
def query__tag_stats(statistics_user: StatisticUser):
    if connection.vendor == "sqlite":
        example_data = {
            "tags": [
                {"tag": "Duldung", "count": 10},
                {"tag": "Abschiebung", "count": 5},
            ],
            "state": [
                {"state": "Set", "count": 10},
                {"state": "Not-Existing", "count": 5},
            ],
        }
        return example_data
    statement = """
    select tag, count(*) as count from (
    select json_array_elements(value::json)::varchar as tag
    from core_datasheetmultipleentry entry
    left join core_datasheetmultiplefield field on entry.field_id = field.id
    where field.name='Tags'
    ) tmp
    group by tag
    order by count(*) desc
    """
    ret = {}
    data = execute_statement(statement)
    data = list(
        map(
            lambda x: {
                "tag": x[0].replace(' "', "").replace('"', ""),
                "count": x[1],
            },
            data,
        )
    )
    ret["tags"] = data
    statement = """
    select name, count(*) as existing
    from (
    select case when name like '%Tags%' then 'Tags' else 'Unknown' end as name
    from (
    select string_agg(name, ' ') as name
    from (
    select record.id,
    case when field.name = 'Tags' then 'Tags' else 'Unknown' end as name
    from core_datasheet record
    left join core_datasheettemplate template on record.template_id = template.id
    left join core_datasheetmultiplefield field on template.id = field.template_id
    ) tmp1
    group by id
    ) tmp2
    ) tmp3
    group by name
    """
    data = execute_statement(statement)
    data = list(map(lambda x: {"state": x[0], "count": x[1]}, data))
    ret["state"] = data
    return ret


class OutputRecordClosedStatistic(BaseModel):
    days: Optional[int]
    count: int


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
            from core_datasheet r
            left join core_datasheetstateentry se on r.id = se.record_id
            where se.value = 'Closed'
            group by round(julianday(se.closed_at) - julianday(r.created) + 1)
            order by days;
        """
    else:
        statement = """
            select
            date_part('day', se.closed_at - r.created) + 1 as days,
            count(*)
            from core_datasheet r
            left join core_datasheetstateentry se on r.id = se.record_id
            where se.value = 'Closed'
            group by date_part('day', se.closed_at - r.created)
            order by days;
        """
    data = execute_statement(statement)
    data = list(map(lambda x: {"days": x[0], "count": x[1]}, data))
    return data


class OutputRecordFieldAmount(BaseModel):
    field: str
    amount: int


@router.api(
    url="record_fields_amount/",
    output_schema=List[OutputRecordFieldAmount],
)
def get_record_fields_amount(statistics_user: StatisticUser):
    statement = """
    select name, count(*) as amount from (
        select name from core_datasheetstatefield
        union all
        select name from core_datasheetstatisticfield
        union all
        select name from core_datasheetencryptedfilefield
        union all
        select name from core_datasheetselectfield
        union all
        select name from core_datasheetencryptedselectfield
        union all
        select name from core_datasheetstandardfield
        union all
        select name from core_datasheetusersfield
        union all
        select name from core_datasheetmultiplefield
        ) t1
    group by name
    order by count(*) desc;
    """
    data = execute_statement(statement)
    data = list(map(lambda x: {"field": x[0], "amount": x[1]}, data))
    return data


class InputRecordStats(BaseModel):
    field_1: str
    value_1: str
    field_2: str


class OutputRecordStats(BaseModel):
    error: bool
    label: str
    data: List[tuple[Any, int, int]]


@router.post(
    url="dynamic/",
    output_schema=OutputRecordStats,
)
def get_dynamic_record_stats(data: InputRecordStats, statistics_user: StatisticUser):
    ret = create_statistic(statistics_user, data.field_1, data.value_1, data.field_2)
    return ret
