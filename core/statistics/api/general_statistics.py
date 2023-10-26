from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

from . import schemas

router = Router()


@router.get("raw_numbers/", output_schema=schemas.OutputRawNumbers)
def query__raw_numbers(statistics_user: StatisticUser):
    statement = """
           select
           (select count(*) as records from core_datasheets) as records,
           (select count(*) as files from core_file) as files,
           (select count(*) as collab from core_collabdocument as collab),
           (select count(*) as users from core_rlcuser as users),
           (select count(*) as lcs from core_org as lcs)
           """
    data = execute_statement(statement)
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
    return data[0]
