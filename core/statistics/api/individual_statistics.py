from django.db import connection

from core.auth.models import RlcUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

from . import schemas

router = Router()


@router.get("user_actions_month/", output_schema=list[schemas.OutputIndividualUserActionsMonth])
def query__user_actions_month(rlc_user: RlcUser):
    if connection.vendor == "sqlite":
        statement = """
            select u.email as email, count(*) as actions
            from core_userprofile as u
            left join core_rlcuser ru on ru.user_id = u.id
            left join core_loggedpath path on u.id = path.user_id
            where path.user_id is not null
            and path.time > date('now', '-1 month')
            and ru.org_id = {}
            group by u.email
            order by count(*) desc;
            """.format(
            rlc_user.org_id
        )
    else:
        statement = """
            select u.email as email, count(*) as actions
            from core_userprofile as u
            left join core_rlcuser ru on ru.user_id = u.id
            left join core_loggedpath path on u.id = path.user_id
            where path.user_id is not null
            and path.time > date_trunc('day', NOW() - interval '1 month')
            and ru.org_id = {}
            group by u.email
            order by count(*) desc;
            """.format(
            rlc_user.org_id
        )
    data = execute_statement(statement)
    data = map(lambda x: {"email": x[0], "actions": x[1]}, data)
    return list(data)
