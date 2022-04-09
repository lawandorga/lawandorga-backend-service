from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from apps.api.models import LoggedPath
from config.authentication import IsAuthenticatedAndEverything
from rest_framework import viewsets
from django.db import connection


class StatisticUserExists(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'statistic_user')


class StatisticViewSet(viewsets.GenericViewSet):
    permission_classes = [StatisticUserExists, IsAuthenticatedAndEverything]
    queryset = LoggedPath.objects.none()

    def execute_statement(self, statement):
        cursor = connection.cursor()
        cursor.execute(statement)
        data = cursor.fetchall()
        return data

    @action(detail=False)
    def rlc_members(self, request, *args, **kwargs):
        statement = """
        select
            api_rlc.name as rlc_name,
            count(distinct api_userprofile.id) as member_amount
        from api_userprofile
        inner join api_rlc on api_rlc.id = api_userprofile.rlc_id
        group by api_userprofile.rlc_id, api_rlc.name;
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {'name': x[0], 'amount': x[1]}, data)
        return Response(data)
