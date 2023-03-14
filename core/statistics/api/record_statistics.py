from typing import List

from django.db import connection

from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from core.statistics.api import schemas
from core.statistics.use_cases.records import create_statistic

router = Router()


@router.get(
    url="record_client_age/",
    output_schema=list[schemas.OutputRecordClientAge],
)
def query__record_client_age(statistics_user: StatisticUser):
    statement = """
            select
            case when entry.value is null then 'Unset' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            where field.name='Age in years of the client' or field.name is null
            group by value
            """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get(
    url="record_client_nationality/",
    output_schema=list[schemas.OutputRecordClientNationality],
)
def query__record_client_nationality(statistics_user: StatisticUser):
    statement = """
            select
            case when entry.value is null then 'Unset' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            where field.name='Nationality of the client' or field.name is null
            group by value
            """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get(
    url="record_client_sex/",
    output_schema=list[schemas.OutputRecordClientSex],
)
def query__record_client_sex(statistics_user: StatisticUser):
    statement = """
            select
            case when entry.value is null then 'Unset' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            where field.name='Sex of the client' or field.name is null
            group by value
            """
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get(
    url="record_states/",
    output_schema=list[schemas.OutputRecordStates],
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
                from core_record as record
                left join core_recordstateentry as state on state.record_id = record.id
                group by record.id, state.record_id, state.value
            ) as tmp
            group by state
            """
    data = execute_statement(statement)
    data = map(lambda x: {"state": x[0], "amount": x[1]}, data)
    return list(data)


@router.get(
    url="tag_stats/",
    output_schema=schemas.OutputRecordTagStats,
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
    from core_recordmultipleentry entry
    left join core_recordmultiplefield field on entry.field_id = field.id
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
    from core_record record
    left join core_recordtemplate template on record.template_id = template.id
    left join core_recordmultiplefield field on template.id = field.template_id
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


@router.api(
    url="records_closed_statistic/",
    output_schema=List[schemas.OutputRecordClosedStatistic],
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
    output_schema=List[schemas.OutputRecordFieldAmount],
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
