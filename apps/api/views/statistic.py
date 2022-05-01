from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response
from config.authentication import IsAuthenticatedAndEverything
from apps.api.models import LoggedPath
from rest_framework import viewsets, status
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

    @action(detail=False)
    def user_actions_month(self, request, *args, **kwargs):
        if settings.DEBUG:
            statement = """
            select u.email as email, count(*) as actions
            from api_userprofile as u
            left join api_loggedpath path on u.id = path.user_id
            where user_id is not null
            and path.time > date('now', '-1 month')
            group by u.email
            order by count(*) desc;
            """
        else:
            statement = """
            select u.email as email, count(*) as actions
            from api_userprofile as u
            left join api_loggedpath path on u.id = path.user_id
            where user_id is not null
            and path.time > date_trunc('day', NOW() - interval '1 month')
            group by u.email
            order by count(*) desc;
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {'email': x[0], 'actions': x[1]}, data)
        return Response(data)

    @action(detail=False)
    def user_logins(self, request, *args, **kwargs):
        statement = """
        select date(time) as date, count(*) as logins
        from api_loggedpath as path
        where path.path like '%login%'
        and (path.status = 200 or path.status = 0)
        group by date(time)
        order by date(time) asc;
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {'date': x[0], 'logins': x[1]}, data)
        return Response(data)

    @action(detail=False)
    def user_logins_month(self, request, *args, **kwargs):
        if settings.DEBUG:
            statement = """
            select strftime('%Y/%m', time) as month, count(*) as logins
            from api_loggedpath as path
            where path.path like '%login%'
            and (path.status = 200 or path.status = 0)
            group by strftime('%Y/%m', time)
            order by date(time) asc;
            """
        else:
            statement = """
            select to_char(time, 'YYYY/MM') as month, count(*) as logins
            from api_loggedpath as path
            where path.path like '%login%'
            and (path.status = 200 or path.status = 0)
            group by to_char(time, 'YYYY/MM')
            order by to_char(time, 'YYYY/MM') asc;
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {'month': x[0], 'logins': x[1]}, data)
        return Response(data)

    # unique users month
    @action(detail=False)
    def unique_users_month(self, request, *args, **kwargs):
        if settings.DEBUG:
            statement = """
            select strftime('%Y/%m', time) as month, count(distinct path.user_id) as logins
            from api_loggedpath as path
            group by strftime('%Y/%m', time)
            order by date(time) asc
            """
        else:
            statement = """
            select to_char(time, 'YYYY/MM') as month, count(distinct path.user_id) as logins
            from api_loggedpath as path
            group by to_char(time, 'YYYY/MM')
            order by to_char(time, 'YYYY/MM') asc;
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {'month': x[0], 'logins': x[1]}, data)
        return Response(data)

    @action(detail=False)
    def errors_month(self, request, *args, **kwargs):
        if settings.DEBUG:
            statement = """
            select status, path, count(*) as count
            from api_loggedpath
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
            from api_loggedpath
            where status > 300
            and status <> 401
            and time > current_date - interval '30' day
            group by status, path
            order by count(*) desc
            limit 20
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {'status': x[0], 'path': x[1], 'count': x[2]}, data)
        return Response(data)

    @action(detail=False)
    def errors_user(self, request, *args, **kwargs):
        statement = """
        select
        email,
        rlckeys.id is not null as rlckeys,
        userkeys.id is not null as userkeys,
        rlcuser.accepted,
        rlcuser.locked
        from api_userprofile baseuser
        inner join api_rlcuser rlcuser on baseuser.id = rlcuser.user_id
        left join api_usersrlckeys rlckeys on baseuser.id = rlckeys.user_id
        left join api_userencryptionkeys userkeys on baseuser.id = userkeys.user_id
        where rlckeys.id is null or userkeys.id is null
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {'email': x[0], 'rlckeys': x[1], 'userkeys': x[2], 'accepted': x[3], 'locked': x[4]}, data)
        return Response(data)

    @action(detail=False)
    def raw_numbers(self, request, *args, **kwargs):
        statement = """
        select
        (select count(*) as records from recordmanagement_record) as records,
        (select count(*) as files from files_file) as files,
        (select count(*) as collab from collab_collabdocument as collab),
        (select count(*) as users from api_rlcuser as users)
        """
        data = self.execute_statement(statement)
        data = list(map(lambda x: {'records': x[0], 'files': x[1], 'collabs': x[2], 'users': x[3]}, data))
        return Response(data[0])

    @action(detail=False)
    def tag_stats(self, request, *args, **kwargs):
        if settings.DEBUG:
            example_data = {
                'tags': [{'tag': 'Duldung', 'count': 10}, {'tag': 'Abschiebung', 'count': 5}],
                'state': [{'state': 'Set', 'count': 10}, {'state': 'Not-Existing', 'count': 5}]
            }
            return Response(example_data)
        statement = """
        select tag, count(*) as count from (
        select json_array_elements(value::json)::varchar as tag
        from recordmanagement_recordmultipleentry entry
        left join recordmanagement_recordmultiplefield field on entry.field_id = field.id
        where field.name='Tags'
        ) tmp
        group by tag
        order by count(*) desc
        """
        ret = {}
        data = self.execute_statement(statement)
        data = list(map(lambda x: {'tag': x[0].replace(' "', '').replace('"', ''), 'count': x[1]}, data))
        ret['tags'] = data
        statement = """
        select name, count(*) as existing
        from (
        select case when name like '%Tags%' then 'Tags' else 'Unknown' end as name
        from (
        select string_agg(name, ' ') as name
        from (
        select record.id,
        case when field.name = 'Tags' then 'Tags' else 'Unknown' end as name
        from recordmanagement_record record
        left join recordmanagement_recordtemplate template on record.template_id = template.id
        left join recordmanagement_recordmultiplefield field on template.id = field.template_id
        ) tmp1
        group by id
        ) tmp2
        ) tmp3
        group by name
        """
        data = self.execute_statement(statement)
        data = list(map(lambda x: {'state': x[0], 'count': x[1]}, data))
        ret['state'] = data
        return Response(ret)

    @action(detail=False)
    def record_client_sex(self, request, *args, **kwargs):
        statement = """
        select
        case when entry.id is null then 'Unknown' else entry.value end as value,
        count(*) as count
        from recordmanagement_record record
        left join recordmanagement_recordstatisticentry entry on record.id = entry.record_id
        left join recordmanagement_recordstatisticfield field on entry.field_id = field.id
        where field.name='Sex of the client' or field.name is null
        group by value
        """
        data = self.execute_statement(statement)
        data = map(lambda x: {'value': x[0], 'count': x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_nationality(self, request, *args, **kwargs):
        statement = """
            select
            case when entry.id is null then 'Unknown' else entry.value end as value,
            count(*) as count
            from recordmanagement_record record
            left join recordmanagement_recordstatisticentry entry on record.id = entry.record_id
            left join recordmanagement_recordstatisticfield field on entry.field_id = field.id
            where field.name='Nationality of the client' or field.name is null
            group by value
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {'value': x[0], 'count': x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_age(self, request, *args, **kwargs):
        statement = """
            select
            case when entry.id is null then 'Unknown' else entry.value end as value,
            count(*) as count
            from recordmanagement_record record
            left join recordmanagement_recordstatisticentry entry on record.id = entry.record_id
            left join recordmanagement_recordstatisticfield field on entry.field_id = field.id
            where field.name='Age in years of the client' or field.name is null
            group by value
            """
        data = self.execute_statement(statement)
        data = map(lambda x: {'value': x[0], 'count': x[1]}, data)
        return Response(data)

    @action(detail=False)
    def record_client_state(self, request, *args, **kwargs):
        statement = """
                select
                case when entry.id is null then 'Unknown' else entry.value end as value,
                count(*) as count
                from recordmanagement_record record
                left join recordmanagement_recordstatisticentry entry on record.id = entry.record_id
                left join recordmanagement_recordstatisticfield field on entry.field_id = field.id
                where field.name='Current Status of the client' or field.name is null
                group by value
                """
        data = self.execute_statement(statement)
        data = map(lambda x: {'value': x[0], 'count': x[1]}, data)
        return Response(data)

