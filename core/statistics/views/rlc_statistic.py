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
