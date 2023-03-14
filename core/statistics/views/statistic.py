from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from config.authentication import IsAuthenticatedAndEverything
from core.models import LoggedPath


class StatisticUserExists(BasePermission):  # type: ignore
    def has_permission(self, request, view):
        return hasattr(request.user, "statistic_user")


class StatisticsViewSet(viewsets.GenericViewSet):
    permission_classes = [StatisticUserExists, IsAuthenticatedAndEverything]
    queryset = LoggedPath.objects.none()

    def execute_statement(self, statement):
        cursor = connection.cursor()
        cursor.execute(statement)
        data = cursor.fetchall()
        return data

    @action(detail=False)
    def raw_numbers(self, request, *args, **kwargs):
        statement = """
        select
        (select count(*) as records from core_record) as records,
        (select count(*) as files from core_file) as files,
        (select count(*) as collab from core_collabdocument as collab),
        (select count(*) as users from core_rlcuser as users),
        (select count(*) as lcs from core_org as lcs)
        """
        data = self.execute_statement(statement)
        data = list(
            map(
                lambda x: {
                    "records": x[0],
                    "files": x[1],
                    "collabs": x[2],
                    "users": x[3],
                    "lcs": x[4],
                },
                data,
            )
        )
        return Response(data[0])

    @action(detail=False)
    def record_client_age(self, request, *args, **kwargs):
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
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_state(self, request, *args, **kwargs):
        statement = """
        select
        case when entry.value is null then 'Unset' else entry.value end as value,
        count(*) as count
        from core_record record
        left join core_recordstatisticentry entry on record.id = entry.record_id
        left join core_recordstatisticfield field on entry.field_id = field.id
        where field.name='Current status of the client' or field.name is null
        group by value
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)
