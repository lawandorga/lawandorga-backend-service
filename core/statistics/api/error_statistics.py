from core.auth.models import StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement

from . import schemas

router = Router()


@router.get("migration/", output_schema=schemas.OutputMigrationStatistic)
def query__migration_statistic(statistics_user: StatisticUser):
    statement = """
    select * from (
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_record
    union all
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_questionnaire
    union all
    select avg(case when folder_uuid is not null then 1 else 0 end), sum(case when folder_uuid is null then 1 else 0 end) as togo
    from core_encryptedrecorddocument
    ) tmp
    """
    data = execute_statement(statement)
    ret = {
        "records": data[0][0],
        "records_togo": data[0][1],
        "questionnaires": data[1][0],
        "questionnaires_togo": data[1][1],
        "documents": data[2][0],
        "documents_togo": data[2][1],
    }
    return ret
