from django.db import connection

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

from . import schemas

router = Router()


@router.get(
    "user_actions_month/", output_schema=list[schemas.OutputIndividualUserActionsMonth]
)
def query__user_actions_month(org_user: OrgUser):
    if connection.vendor == "sqlite":
        statement = """
            select u.email as email, count(*) as actions
            from core_userprofile as u
            left join core_orguser ru on ru.user_id = u.id
            left join core_loggedpath path on u.id = path.user_id
            where path.user_id is not null
            and path.time > date('now', '-1 month')
            and ru.org_id = {}
            group by u.email
            order by count(*) desc;
            """.format(
            org_user.org_id
        )
    else:
        statement = """
            select u.email as email, count(*) as actions
            from core_userprofile as u
            left join core_orguser ru on ru.user_id = u.id
            left join core_loggedpath path on u.id = path.user_id
            where path.user_id is not null
            and path.time > date_trunc('day', NOW() - interval '1 month')
            and ru.org_id = {}
            group by u.email
            order by count(*) desc;
            """.format(
            org_user.org_id
        )
    data = execute_statement(statement)
    data = map(lambda x: {"email": x[0], "actions": x[1]}, data)
    return list(data)


@router.get("record_states/", output_schema=list[schemas.OutputRecordStates])
def query__record_states(org_user: OrgUser):
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
                 left join core_datasheettemplate as template on template.id = record.template_id
                 where template.rlc_id = {}
                 group by record.id, state.record_id, state.value
             ) as tmp
             group by state
             """.format(
        org_user.org_id
    )
    data = execute_statement(statement)
    data = map(lambda x: {"state": x[0], "amount": x[1]}, data)
    return list(data)


@router.get("record_client_age/", output_schema=list[schemas.OutputRecordClientAge])
def query__record_client_age(org_user: OrgUser):
    statement = """
                select
                case when entry.value is null then 'Not-Set' else entry.value end as value,
                count(*) as count
                from core_datasheet record
                left join core_datasheetstatisticentry entry on record.id = entry.record_id
                left join core_datasheetstatisticfield field on entry.field_id = field.id
                left join core_datasheettemplate as template on template.id = record.template_id
                where (field.name='Age in years of the client' or field.name is null) and template.rlc_id = {}
                group by value
                """.format(
        org_user.org_id
    )
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get(
    "record_client_nationality/",
    output_schema=list[schemas.OutputRecordClientNationality],
)
def query__record_client_nationality(org_user: OrgUser):
    statement = """
           select
           case when entry.value is null then 'Not-Set' else entry.value end as value,
           count(*) as count
           from core_datasheet record
           left join core_datasheetstatisticentry entry on record.id = entry.record_id
           left join core_datasheetstatisticfield field on entry.field_id = field.id
           left join core_datasheettemplate as template on template.id = record.template_id
           where (field.name='Nationality of the client' or field.name is null) and template.rlc_id = {}
           group by value
           """.format(
        org_user.org_id
    )
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get("record_client_state/", output_schema=list[schemas.OutputRecordClientState])
def query__record_client_state(org_user: OrgUser):
    statement = """
                select
                case when entry.value is null then 'Not-Set' else entry.value end as value,
                count(*) as count
                from core_datasheet record
                left join core_datasheetstatisticentry entry on record.id = entry.record_id
                left join core_datasheetstatisticfield field on entry.field_id = field.id
                left join core_datasheettemplate as template on template.id = record.template_id
                where (field.name='Current status of the client' or field.name is null) and template.rlc_id = {}
                group by value
                """.format(
        org_user.org_id
    )
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get("record_client_sex/", output_schema=list[schemas.OutputRecordClientSex])
def query__record_client_sex(org_user: OrgUser):
    statement = """
               select
               case when entry.value is null then 'Not-Set' else entry.value end as value,
               count(*) as count
               from core_datasheet record
               left join core_datasheetstatisticentry entry on record.id = entry.record_id
               left join core_datasheetstatisticfield field on entry.field_id = field.id
               left join core_datasheettemplate as template on template.id = record.template_id
               where (field.name='Sex of the client' or field.name is null) and template.rlc_id = {}
               group by value
               """.format(
        org_user.org_id
    )
    data = execute_statement(statement)
    data = map(lambda x: {"value": x[0], "count": x[1]}, data)
    return list(data)


@router.get("tag_stats/", output_schema=schemas.OutputRecordTagStats)
def query__tag_stats(org_user: OrgUser):
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
        left join core_datasheettemplate as template on template.id = field.template_id
        where field.name='Tags'
        and template.rlc_id = {}
        ) tmp
        group by tag
        order by count(*) desc
        """.format(
        org_user.org_id
    )
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
        where template.rlc_id = {}
        ) tmp1
        group by id
        ) tmp2
        ) tmp3
        group by name
        """.format(
        org_user.org_id
    )
    data = execute_statement(statement)
    data = list(map(lambda x: {"state": x[0], "count": x[1]}, data))
    ret["state"] = data
    return ret
