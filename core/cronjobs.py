from core.seedwork.api_layer import Router
from core.seedwork.cronjobs import CronjobWarehouse

router = Router()


@router.api(url="run/", output_schema=dict)
def run_cronjobs():
    CronjobWarehouse.run_cronjobs()
    return {"status": "OK"}


@router.api(url="status/", output_schema=dict[str, list[str]])
def get_status():
    return CronjobWarehouse.get_runs()
