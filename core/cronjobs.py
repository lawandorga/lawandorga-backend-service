from asgiref.sync import sync_to_async

from core.seedwork.api_layer import Router
from core.seedwork.cronjobs import CronjobWarehouse

router = Router()


@router.api(url="run/", output_schema=dict)
async def run_cronjobs():
    await sync_to_async(CronjobWarehouse.run_cronjobs)()
    return {"status": "OK"}


@router.api(url="status/", output_schema=dict[str, list[str]])
def get_status():
    return CronjobWarehouse.get_runs()
