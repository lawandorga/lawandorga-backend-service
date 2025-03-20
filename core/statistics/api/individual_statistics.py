from django.db import connection
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.data_sheets.models.data_sheet import DataSheet
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from core.statistics.api.utils import get_available_datasheet_years

from . import schemas
from seedwork.functional import list_filter

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


class TagStatsInput(BaseModel):
    year: str | None = None


class OutputTagStats(BaseModel):
    stats: dict[str, int]
    years: list[int]


@router.get("tag_stats/", output_schema=OutputTagStats)
def query__tag_stats(org_user: OrgUser, data: TagStatsInput):
    stats: dict[str, int] = {"Not Set": 0}

    qs = DataSheet.objects.filter(template__rlc_id=org_user.org_id).prefetch_related(
        "template",
        "multiple_entries",
        "multiple_entries__field",
        "template__multiple_fields",
        "template__multiple_fields__entries",
    )

    if data.year:
        qs = qs.filter(created__year=data.year)

    sheets = list(qs)
    for sheet in sheets:
        fields = list(sheet.template.multiple_fields.all())
        entries = list(sheet.multiple_entries.all())

        tag_fields = list_filter(fields, lambda f: "tags" in f.name.lower())
        for entry in entries:
            if entry.field not in tag_fields:
                continue
            for v in entry.value:
                stats[v] = stats.get(v, 0) + 1

        for field in tag_fields:
            entries = list(field.entries.all())
            sheet_entries = list_filter(entries, lambda e: e.record_id == sheet.pk)
            if not sheet_entries:
                stats["Not Set"] += 1
            elif sum([len(e.value) for e in sheet_entries]) == 0:
                stats["Not Set"] += 1

    years = get_available_datasheet_years(org_user.org_id)

    ret = {
        "stats": stats,
        "years": years,
    }

    return ret
