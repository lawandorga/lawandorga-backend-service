from logging import INFO, WARNING, getLogger
from typing import Any, Callable, Type, TypeVar, get_type_hints

from django.core.exceptions import ObjectDoesNotExist

from apps.static.domain_layer import DomainError

logger = getLogger("usecase")

T = TypeVar("T", bound=type)
K = TypeVar("K", bound=object)
F = TypeVar("F", bound=Callable[[K, Any], T])

MAPPINGS = dict[T, F]()


def add_mapping(t: Type[K], func: Callable[[Any, Any], K]):
    if t in MAPPINGS:
        raise Exception("Type '{}' already has a mapping.".format(t))
    MAPPINGS[t] = func


class UseCaseError(Exception):
    def __init__(self, message):
        self.message = message


class UseCaseInputError(Exception):
    def __init__(self, message):
        self.message = message


__all__ = ["use_case", "add_mapping", "UseCaseError", "UseCaseInputError"]


def __check_actor(kwargs, func_code, type_hints):
    if "__actor" not in kwargs:
        raise Exception("You need to submit an '__actor' when calling a usecase.")

    if "__actor" not in func_code.co_varnames:
        raise Exception("The usecase needs to define an '__actor' as argument.")

    if "__actor" not in type_hints:
        raise Exception("The usecase needs a type hint to '__actor'.")

    actor = kwargs["__actor"]

    submitted_actor_type = type(actor)
    usecase_actor_type = type_hints["__actor"]
    if submitted_actor_type != usecase_actor_type:
        raise Exception(
            "The use case '__actor' type is '{}' but should be '{}'.".format(
                submitted_actor_type, usecase_actor_type
            )
        )

    return actor


def __check_type(value, type_hint):
    value_type = type(value)
    if value_type != type_hint:
        raise Exception(
            "The type of '{}' is '{}' but should be '{}'.".format(
                value, value_type, type_hint
            )
        )


def __update_parameters(args, kwargs, func_code, type_hints, actor):
    args = list(args)

    i = 0
    for param in func_code.co_varnames[: func_code.co_argcount]:

        if len(args) > i:
            value = args[i]
        else:
            value = kwargs[param]

        if param in type_hints:
            type_hint = type_hints[param]

            if param != "__actor" and type_hint in MAPPINGS:
                try:
                    replacement = MAPPINGS[type_hint](value, actor)
                except ObjectDoesNotExist as e:
                    message = "The object of type '{}' with identifier '{}' could not be found.".format(
                        type_hint, value
                    )
                    raise UseCaseInputError(message) from e
            else:
                replacement = value

            __check_type(replacement, type_hint)

            if len(args) > i:
                args[i] = replacement
            else:
                kwargs[param] = replacement

        i += 1

    return args, kwargs


def __check_permissions(actor, permissions):
    for permission in permissions:
        if not actor.has_permission(permission):
            message = "You need the permission '{}' to do this.".format(permission)
            raise UseCaseError(message)


def use_case(permissions=None):
    if permissions is None:
        permissions = []

    def wrapper(usecase_func):
        type_hints = get_type_hints(usecase_func)

        def execute(*args, **kwargs):
            func_code = usecase_func.__code__
            func_name = func_code.co_name

            actor = __check_actor(kwargs, func_code, type_hints)

            __check_permissions(actor, permissions)

            args, kwargs = __update_parameters(
                args, kwargs, func_code, type_hints, actor
            )

            try:
                ret = usecase_func(*args, **kwargs)
                msg = "SUCCESS: '{}' called '{}'.".format(str(actor), func_name)
                logger.log(INFO, msg)
                return ret
            except (UseCaseError, DomainError) as e:
                msg = "ERROR: '{}' called '{}' and '{}' happened.".format(
                    str(actor), func_name, str(e)
                )
                logger.log(WARNING, msg)
                raise e

        return execute

    return wrapper
