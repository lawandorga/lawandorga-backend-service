import importlib
from typing import Callable

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone

from core.seedwork.api_layer import Router

router = Router()


class CronjobWarehouse:
    __CRONJOBS: list[Callable[[], str]] = []
    __RUNS: dict[str, list[str]] = {}

    @classmethod
    def setup_cronjobs(cls):
        if len(cls.__CRONJOBS) == 0:
            for s in settings.CRONJOBS:
                module_name = ".".join(s.split(".")[:-1])
                module = importlib.import_module(module_name)
                function_name = s.split(".")[-1]
                job = getattr(module, function_name)
                cls.add_cronjob(job)

    @classmethod
    def add_cronjob(cls, job: Callable[[], str]):
        cls.__CRONJOBS.append(job)

    @classmethod
    async def run_cronjobs(cls):
        cls.setup_cronjobs()
        results = []
        for job in cls.__CRONJOBS:
            try:
                result = await sync_to_async(job, thread_sensitive=False)()
            except Exception as e:
                result = "ERROR {}".format(str(e))
            results.append(result)
        cls.__RUNS[timezone.now().strftime("%Y-%m-%d---%H:%M:%S")] = results

    @classmethod
    def status(cls):
        return cls.__RUNS


@router.api(url="run/", output_schema=dict)
async def run_cronjobs():
    # loop = asyncio.get_event_loop()
    # loop.create_task(CronjobWarehouse.run_cronjobs())
    await CronjobWarehouse.run_cronjobs()
    return {"status": "OK"}


@router.api(url="status/", output_schema=dict[str, list[str]])
def status():
    return CronjobWarehouse.status()
