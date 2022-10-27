import asyncio
import importlib
from typing import Awaitable, Callable, Optional

from django.conf import settings
from django.utils import timezone

from core.seedwork.api_layer import Router

router = Router()


class CronjobWarehouse:
    __CRONJOBS: list[Callable[[], Awaitable[str]]] = []
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
    def add_cronjob(cls, job: Callable[[], Awaitable[str]]):
        cls.__CRONJOBS.append(job)

    @classmethod
    async def run_cronjobs(cls):
        cls.setup_cronjobs()
        jobs = [f() for f in cls.__CRONJOBS]
        results = await asyncio.gather(*jobs)
        cls.__RUNS[timezone.now().strftime("%Y-%m-%d---%H:%M:%S")] = results

    @classmethod
    def status(cls):
        return cls.__RUNS


@router.api(url="run/", output_schema=dict)
async def run_cronjobs():
    loop = asyncio.get_event_loop()
    loop.create_task(CronjobWarehouse.run_cronjobs())
    return {"status": "OK"}


@router.api(url="status/", output_schema=dict[str, list[Optional[str]]])
def status():
    return CronjobWarehouse.status()
