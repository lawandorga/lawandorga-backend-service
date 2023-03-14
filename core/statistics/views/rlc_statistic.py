from django.conf import settings
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class RlcStatisticsViewSet(viewsets.GenericViewSet):
    def execute_statement(self, statement):
        assert str(self.request.user.rlc.id) in statement
        cursor = connection.cursor()
        cursor.execute(statement)
        data = cursor.fetchall()
        return data

    @action(detail=False)
    def record_states(self, request, *args, **kwargs):
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
             left join core_recordtemplate as template on template.id = record.template_id
             where template.rlc_id = {}
             group by record.id, state.record_id, state.value
         ) as tmp
         group by state
         """.format(
            request.user.rlc.id
        )
        data = self.execute_statement(statement)
        data = map(lambda x: {"state": x[0], "amount": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def tag_stats(self, request, *args, **kwargs):
        if settings.DEBUG:
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
            return Response(example_data)
        statement = """
            select tag, count(*) as count from (
            select json_array_elements(value::json)::varchar as tag
            from core_recordmultipleentry entry
            left join core_recordmultiplefield field on entry.field_id = field.id
            left join core_recordtemplate as template on template.id = field.template_id
            where field.name='Tags'
            and template.rlc_id = {}
            ) tmp
            group by tag
            order by count(*) desc
            """.format(
            request.user.rlc.id
        )
        ret = {}
        data = self.execute_statement(statement)
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
            where template.rlc_id = {}
            ) tmp1
            group by id
            ) tmp2
            ) tmp3
            group by name
            """.format(
            request.user.rlc.id
        )
        data = self.execute_statement(statement)
        data = list(map(lambda x: {"state": x[0], "count": x[1]}, data))
        ret["state"] = data
        return Response(ret)

    @action(detail=False)
    def record_client_sex(self, request, *args, **kwargs):
        statement = """
            select
            case when entry.value is null then 'Unknown' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            left join core_recordtemplate as template on template.id = field.template_id
            where (field.name='Sex of the client' or field.name is null) and template.rlc_id = {}
            group by value
            """.format(
            request.user.rlc.id
        )
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_nationality(self, request, *args, **kwargs):
        statement = """
            select
            case when entry.value is null then 'Unknown' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            left join core_recordtemplate as template on template.id = field.template_id
            where (field.name='Nationality of the client' or field.name is null) and template.rlc_id = {}
            group by value
            """.format(
            request.user.rlc.id
        )
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_age(self, request, *args, **kwargs):
        statement = """
            select
            case when entry.value is null then 'Unknown' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            left join core_recordtemplate as template on template.id = field.template_id
            where (field.name='Age in years of the client' or field.name is null) and template.rlc_id = {}
            group by value
            """.format(
            request.user.rlc.id
        )
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_state(self, request, *args, **kwargs):
        statement = """
            select
            case when entry.value is null then 'Unknown' else entry.value end as value,
            count(*) as count
            from core_record record
            left join core_recordstatisticentry entry on record.id = entry.record_id
            left join core_recordstatisticfield field on entry.field_id = field.id
            left join core_recordtemplate as template on template.id = field.template_id
            where (field.name='Current status of the client' or field.name is null) and template.rlc_id = {}
            group by value
            """.format(
            request.user.rlc.id
        )
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)
