from functools import wraps
from logging import getLogger
from typing import Any, Callable, TypeVar, get_type_hints, overload

from django.conf import settings
from django.utils.module_loading import import_string
from pydantic import validate_call

from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer.callbacks import CallbackContext
from core.seedwork.use_case_layer.checks import __check_actor, check_permissions
from core.seedwork.use_case_layer.error import UseCaseError
from core.seedwork.use_case_layer.injector import (
    InjectionContext,
    inject_kwargs,
)

logger = getLogger("usecase")

injections = import_string(settings.USECASE_INJECTIONS)
DJANGO_INJECTION_CONTEXT = InjectionContext(injections)
DJANGO_CALLBACKS = import_string(settings.USECASE_CALLBACKS)

RetType = TypeVar("RetType")


@overload
def use_case(
    func: Callable[..., RetType],
    *,
    permissions: None = ...,
    context: InjectionContext = ...,
    callbacks: list[Callable[..., Any]] = ...,
) -> Callable[..., RetType]: ...


@overload
def use_case(
    func: None = ...,
    *,
    permissions: list[str] | None = ...,
    context: InjectionContext = ...,
    callbacks: list[Callable[..., Any]] = ...,
) -> Callable[[Callable[..., RetType]], Callable[..., RetType]]: ...


def use_case(
    func: Callable[..., RetType] | None = None,
    *,
    permissions: list[str] | None = None,
    context: InjectionContext = DJANGO_INJECTION_CONTEXT,
    callbacks: list[Callable[..., Any]] = DJANGO_CALLBACKS,
) -> (
    Callable[..., RetType] | Callable[[Callable[..., RetType]], Callable[..., RetType]]
):
    if permissions is None:
        permissions = []

    def decorator(usecase_func: Callable[..., RetType]) -> Callable[..., RetType]:
        type_hints = get_type_hints(usecase_func)

        @wraps(usecase_func)
        def wrapper(*args, **kwargs) -> RetType:
            context.reset()
            kwargs = inject_kwargs(usecase_func, kwargs, context)

            func_code = usecase_func.__code__
            func_name = func_code.co_name

            actor = __check_actor(args, kwargs, func_code, type_hints)

            check_permissions(actor, permissions)

            callback_context = CallbackContext(
                success=True, actor=actor, fn_name=func_name
            )
            context.injections[CallbackContext] = callback_context

            def run_callbacks():
                for callback in callbacks:
                    callback(
                        **inject_kwargs(
                            callback,
                            {},
                            context,
                        )
                    )

            try:
                ret = validate_call(config={"arbitrary_types_allowed": True})(
                    usecase_func
                )(*args, **kwargs)
                msg = "SUCCESS: '{}' called '{}'.".format(str(actor), func_name)
                logger.info(msg)
                run_callbacks()
                return ret
            except (UseCaseError, DomainError) as e:
                callback_context.success = False
                msg = "ERROR: '{}' called '{}' and '{}' happened.".format(
                    str(actor), func_name, str(e)
                )
                logger.warning(msg)
                run_callbacks()
                raise e

        return wrapper

    if func:
        # this happens when use_case is used like @use_case instead of @use_case()
        return decorator(func)

    return decorator
