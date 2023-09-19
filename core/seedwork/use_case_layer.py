from functools import wraps
from logging import INFO, WARNING, getLogger
from typing import Callable, ParamSpec, TypeVar, get_type_hints, overload

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.module_loading import import_string

from core.seedwork.domain_layer import DomainError

from seedwork.injector import InjectionContext, inject_function

logger = getLogger("usecase")

T = TypeVar("T")


injections = import_string(settings.USECASE_INJECTIONS)
inj_context = InjectionContext(injections)


class UseCaseError(Exception):
    def __init__(self, message):
        self.message = message


class UseCaseInputError(Exception):
    def __init__(self, message):
        self.message = message


P1 = ParamSpec("P1")
T1 = TypeVar("T1")


def finder_function(function: Callable[P1, T1]) -> Callable[P1, T1]:
    def decorator(*args: P1.args, **kwargs: P1.kwargs):
        try:
            return function(*args, **kwargs)
        except ObjectDoesNotExist:
            message = "The object could not be found."
            raise UseCaseInputError(message)

    return decorator


__all__ = [
    "use_case",
    "check_permissions",
    "finder_function",
    "UseCaseError",
    "UseCaseInputError",
]


def __check_actor(args, kwargs, func_code, type_hints):
    if len(func_code.co_varnames) == 0 or "__actor" not in func_code.co_varnames:
        raise ValueError("The use case function needs to have '__actor' as input.")

    if "__actor" not in type_hints:
        raise ValueError("The usecase needs a type hint to '__actor'.")

    if "__actor" in kwargs:
        actor = kwargs["__actor"]
    elif len(args) > 0:
        index = func_code.co_varnames.index("__actor")
        actor = args[index]
    else:
        raise ValueError(
            "You need to submit an '__actor' when you call a use case function."
        )

    usecase_actor_type = type_hints["__actor"]
    if not isinstance(actor, usecase_actor_type):
        raise TypeError(
            "The submitted use case '__actor' type is '{}' but should be '{}'.".format(
                type(actor), usecase_actor_type
            )
        )

    return actor


def check_permissions(actor, permissions, message_addition=""):
    assert isinstance(permissions, list)
    for permission in permissions:
        if not actor.has_permission(permission):
            message = "You need the permission '{}' to do this.".format(permission)
            if message_addition:
                message = "{} {}".format(message, message_addition)
            raise UseCaseError(message)


RetType = TypeVar("RetType")


@overload
def use_case(
    func: Callable[..., RetType],
    *,
    permissions: None = ...,
) -> Callable[..., RetType]:
    ...


@overload
def use_case(
    func: None = ...,
    *,
    permissions: list[str] | None = ...,
) -> Callable[[Callable[..., RetType]], Callable[..., RetType]]:
    ...


def use_case(
    func: Callable[..., RetType] | None = None,
    *,
    permissions: list[str] | None = None,
) -> (
    Callable[..., RetType] | Callable[[Callable[..., RetType]], Callable[..., RetType]]
):
    if permissions is None:
        permissions = []

    def decorator(usecase_func: Callable[..., RetType]) -> Callable[..., RetType]:
        type_hints = get_type_hints(usecase_func)
        injected_usecase_func = inject_function(usecase_func, inj_context)
        injected_usecase_func.__annotations__ = usecase_func.__annotations__

        @wraps(injected_usecase_func)
        def wrapper(*args, **kwargs) -> RetType:
            func_code = usecase_func.__code__
            func_name = func_code.co_name

            actor = __check_actor(args, kwargs, func_code, type_hints)

            check_permissions(actor, permissions)

            try:
                ret = injected_usecase_func(*args, **kwargs)
                msg = "SUCCESS: '{}' called '{}'.".format(str(actor), func_name)
                logger.log(INFO, msg)
                return ret
            except (UseCaseError, DomainError) as e:
                msg = "ERROR: '{}' called '{}' and '{}' happened.".format(
                    str(actor), func_name, str(e)
                )
                logger.log(WARNING, msg)
                raise e

        return wrapper

    if func:
        # this happens when use_case is used like @use_case instead of @use_case()
        return decorator(func)

    return decorator
