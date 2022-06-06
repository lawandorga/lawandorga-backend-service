from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.db import connection


class RlcStatisticViewSet(viewsets.GenericViewSet):
    def execute_statement(self, statement):
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
               from recordmanagement_record as record
               left join recordmanagement_recordstateentry as state on state.record_id = record.id
               group by record.id, state.record_id, state.value
           ) as tmp
           group by state
           """
        data = self.execute_statement(statement)
        data = map(lambda x: {'state': x[0], 'amount': x[1]}, data)
        return Response({})
