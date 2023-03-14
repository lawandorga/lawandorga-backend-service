from django.conf import settings
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
            group by record.id, state.record_id, state.value
        ) as tmp
        group by state
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {"state": x[0], "amount": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def errors_month(self, request, *args, **kwargs):
        if settings.DEBUG:
            statement = """
            select status, path, count(*) as count
            from core_loggedpath
            where status > 300
            and status <> 401
            and time > date('now', '-1 month')
            group by status, path
            order by count(*) desc
            limit 20
            """
        else:
            statement = """
            select status, path, count(*) as count
            from core_loggedpath
            where status > 300
            and status <> 401
            and time > current_date - interval '30' day
            group by status, path
            order by count(*) desc
            limit 20
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {"status": x[0], "path": x[1], "count": x[2]}, data)
        return Response(data)

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
        where field.name='Tags'
        ) tmp
        group by tag
        order by count(*) desc
        """
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
        ) tmp1
        group by id
        ) tmp2
        ) tmp3
        group by name
        """
        data = self.execute_statement(statement)
        data = list(map(lambda x: {"state": x[0], "count": x[1]}, data))
        ret["state"] = data
        return Response(ret)

    @action(detail=False)
    def record_client_sex(self, request, *args, **kwargs):
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
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_nationality(self, request, *args, **kwargs):
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
        data = self.execute_statement(statement)
        data = map(lambda x: {"value": x[0], "count": x[1]}, data)
        return Response(data)

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

    @action(detail=False)
    def users_with_missing_access(self, request, *args, **kwargs):
        statement = """
        select u, r, enc
        from (
                 select u.id                   as u,
                        count(distinct r.id)   as r,
                        count(distinct enc.id) as enc

                 from core_userprofile u
                          cross join core_record r

                          left join core_recordencryptionnew enc
                                    on enc.user_id = u.id and enc.record_id = r.id

                          left join core_recordtemplate t on t.id = r.template_id
                          left join core_group_group_members cggm on u.id = cggm.userprofile_id
                          left join core_haspermission ch1 on u.id = ch1.user_has_permission_id
                          left join core_haspermission ch2 on cggm.group_id = ch2.group_has_permission_id
                          left join core_permission cp1 on cp1.id = ch1.permission_id
                          left join core_permission cp2 on cp2.id = ch2.permission_id
                 where (cp1.name = 'records__access_all_records' or cp2.name = 'records__access_all_records')
                   and t.rlc_id = u.rlc_id
                 group by u.id
             ) t1
        where r<>enc;
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {"user": x[0], "records": x[1], "access": x[2]}, data)
        return Response(data)
