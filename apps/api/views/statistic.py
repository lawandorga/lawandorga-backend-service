from rest_framework.permissions import BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response
from config.authentication import IsAuthenticatedAndEverything
from apps.api.models import LoggedPath
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
        return Response(data)

    @action(detail=False)
    def lc_usage(self, request, *args, **kwargs):
        statement = """
        select
            rlc.name as name,
            count(distinct record.id) as records,
            count(distinct file.id) as files,
            count(distinct document.id) as documents
        from api_rlc as rlc
        left join recordmanagement_recordtemplate template on rlc.id = template.rlc_id
        left join recordmanagement_record record on record.template_id = template.id
        left join files_folder folder on rlc.id = folder.rlc_id
        left join files_file file on file.folder_id = folder.id
        left join collab_collabdocument document on rlc.id = document.rlc_id
        group by rlc.id, rlc.name;
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {'lc': x[0], 'records': x[1], 'files': x[2], 'documents': x[3]}, data)
        return Response(data)
