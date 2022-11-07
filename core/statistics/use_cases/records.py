from core.auth.models import StatisticUser
from core.seedwork.statistics import execute_statement
from core.seedwork.use_case_layer import UseCaseError, use_case


def clean_str(v):
    return "".join(
        ch
        for ch in v
        if ch.isalnum() or ch == " " or ch == "%" or ch == "-" or ch == "_"
    )


@use_case()
def create_statistic(__actor: StatisticUser, field_1: str, value_1: str, field_2: str):
    cleaned_field_1 = clean_str(field_1)
    cleaned_value_1 = clean_str(value_1)
    cleaned_field_2 = clean_str(field_2)

    if (
        field_1 != cleaned_field_1
        or value_1 != cleaned_value_1
        or cleaned_field_2 != field_2
    ):
        raise UseCaseError(
            "Your input contains illegal characters. "
            "Only a-z, A-Z, 0-9, %, -, _ and space is allowed."
        )

    statement = """
    with t as (
        select id, name as field, value from
        core_record record
        left join (

            select name, value, record_id
            from core_recordstatefield state_field
            inner join core_recordstateentry state_entry on state_field.id = state_entry.field_id
            union all
            select name, value, record_id from core_recordstatisticfield statistic_field
            inner join core_recordstatisticentry statistic_entry on statistic_field.id = statistic_entry.field_id
            union all
            select name, value, record_id from core_recordselectfield select_field
            inner join core_recordselectentry select_entry on select_field.id = select_entry.field_id
            union all
            select name, value, record_id
            from core_recordstandardfield standard_field
            inner join core_recordstandardentry standard_entry on standard_field.id = standard_entry.field_id

        ) k on k.record_id = record.id
    )

    select value, count(*) as count, max(error) as error
    from (
        select t1.id, t2.value as value, count(*) as count, COUNT('x') over (partition by t1.id) - 1 as error
        from t t1
        inner join t t2 on t1.id = t2.id
        where (lower(t1.field) like lower('{}') and lower(t1.value) like lower('{}')) and lower(t2.field) = lower('{}')
        group by t1.id, t2.value
    ) m
    group by value;
    """.format(
        cleaned_field_1, cleaned_value_1, cleaned_field_2
    )
    data = execute_statement(statement)
    error = bool(sum(map(lambda x: x[2], data)))
    ret = {
        "label": "Statistic about '{}' on all records that have the field '{}' with value '{}'".format(
            cleaned_field_2, cleaned_field_1, cleaned_value_1
        ),
        "data": data,
        "error": error,
    }
    return ret
