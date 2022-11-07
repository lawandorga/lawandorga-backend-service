import importlib
from typing import Callable

from django.conf import settings
from django.utils import timezone

from core.seedwork.api_layer import Router

router = Router()


class CronjobWarehouse:
    __CRONJOBS: list[Callable[[], str]] = []
    __RUNS: dict[str, list[str]] = {}

    @classmethod
    def __setup_cronjobs(cls):
        if len(cls.__CRONJOBS) == 0:
            for s in settings.CRONJOBS:
                module_name = ".".join(s.split(".")[:-1])
                module = importlib.import_module(module_name)
                function_name = s.split(".")[-1]
                job: Callable[[], str] = getattr(module, function_name)
                cls.__add_cronjob(job)

    @classmethod
    def __add_cronjob(cls, job: Callable[[], str]):
        cls.__CRONJOBS.append(job)

    @classmethod
    def run_cronjobs(cls):
        cls.__setup_cronjobs()
        results = []
        for job in cls.__CRONJOBS:
            try:
                result = job()
            except Exception as e:
                result = "ERROR {}".format(str(e))
            status = "{}: {}".format(job.__code__.co_name, result)
            results.append(status)
        cls.__RUNS[timezone.now().strftime("%Y-%m-%d---%H:%M:%S")] = results
        return results

    @classmethod
    def get_runs(cls):
        return cls.__RUNS
