from typing import Callable, ParamSpec, TypeVar

from django.core.exceptions import ObjectDoesNotExist

from core.seedwork.use_case_layer.error import UseCaseError

P1 = ParamSpec("P1")
T1 = TypeVar("T1")


def finder_function(function: Callable[P1, T1]) -> Callable[P1, T1]:
    def decorator(*args: P1.args, **kwargs: P1.kwargs):
        try:
            return function(*args, **kwargs)
        except ObjectDoesNotExist:
            message = "The object could not be found."
            raise UseCaseError(message)

    return decorator
