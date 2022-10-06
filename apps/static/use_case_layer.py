from logging import INFO, WARNING, getLogger
from typing import Callable, TypeVar, Union, get_type_hints

from django.core.exceptions import ObjectDoesNotExist

from apps.static.domain_layer import DomainError

logger = getLogger("usecase")

T = TypeVar("T", bound=type)
K = TypeVar("K", bound=object)
F = TypeVar("F", bound=Callable[[K], Union[T, K]])

MAPPINGS = dict[T, F]()


def add_mapping(t: T, func: F):
    if t in MAPPINGS:
        raise Exception("Type '{}' already has a mapping.".format(t))
    MAPPINGS[t] = func


class UseCaseError(Exception):
    def __init__(self, message):
        self.message = message


class InputError(Exception):
    def __init__(self, message):
        self.message = message


__all__ = ["use_case", "add_mapping", "UseCaseError", "InputError"]


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


def __update_parameters(args, kwargs, func_code, type_hints):
    args = list(args)

    i = 0
    for param in func_code.co_varnames:

        if len(args) > i:
            value = args[i]
        else:
            value = kwargs[param]

        if param in type_hints:
            type_hint = type_hints[param]
            if type_hint in MAPPINGS:

                try:
                    replacement = MAPPINGS[type_hint](value)
                except ObjectDoesNotExist as e:
                    message = (
                        "The object with identifier '{}' could not be found.".format(
                            value
                        )
                    )
                    raise InputError(message) from e

                if len(args) > i:
                    args[i] = replacement
                else:
                    kwargs[param] = replacement
            else:
                value_type = type(value)
                if value_type != type_hint:
                    raise Exception(
                        "The type of '{}' is '{}' but should be '{}'.".format(
                            param, value_type, type_hint
                        )
                    )
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

            args, kwargs = __update_parameters(args, kwargs, func_code, type_hints)

            try:
                usecase_func(*args, **kwargs)
                msg = "SUCCESS: '{}' called '{}'.".format(str(actor), func_name)
                logger.log(INFO, msg)
            except (UseCaseError, DomainError) as e:
                msg = "ERROR: '{}' called '{}' and '{}' happened.".format(
                    str(actor), func_name, str(e)
                )
                logger.log(WARNING, msg)
                raise e

        return execute

    return wrapper
