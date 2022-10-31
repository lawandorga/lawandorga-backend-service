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
                job: Callable[[], str] = getattr(module, function_name)
                cls.add_cronjob(job)

    @classmethod
    def add_cronjob(cls, job: Callable[[], str]):
        cls.__CRONJOBS.append(job)

    @classmethod
    def run_cronjobs(cls):
        cls.setup_cronjobs()
        results = []
        for job in cls.__CRONJOBS:
            try:
                result = job()
            except Exception as e:
                result = "ERROR {}".format(str(e))
            status = '{}: {}'.format(job.__code__.co_name, result)
            results.append(status)
        cls.__RUNS[timezone.now().strftime("%Y-%m-%d---%H:%M:%S")] = results
        return results

    @classmethod
    def get_runs(cls):
        return cls.__RUNS


@router.api(url="run/", output_schema=dict)
async def run_cronjobs():
    await sync_to_async(CronjobWarehouse.run_cronjobs)()
    return {"status": "OK"}


@router.api(url="status/", output_schema=dict[str, list[str]])
def get_status():
    return CronjobWarehouse.get_runs()
