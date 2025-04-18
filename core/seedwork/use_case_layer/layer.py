from functools import wraps
from logging import INFO, WARNING, getLogger
from typing import Callable, TypeVar, get_type_hints, overload

from django.conf import settings
from django.utils.module_loading import import_string
from pydantic import validate_call

from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer.callbacks import CallbackContext
from core.seedwork.use_case_layer.checks import __check_actor, check_permissions
from core.seedwork.use_case_layer.error import UseCaseError
from core.seedwork.use_case_layer.injector import (
    CallableInjectionContext,
    InjectionContext,
    inject_function,
    inject_kwargs,
)

logger = getLogger("usecase")

injections = import_string(settings.USECASE_INJECTIONS)
inj_context = InjectionContext(injections)


callbacks = import_string(settings.USECASE_CALLBACKS)

RetType = TypeVar("RetType")


@overload
def use_case(
    func: Callable[..., RetType],
    *,
    permissions: None = ...,
) -> Callable[..., RetType]: ...


@overload
def use_case(
    func: None = ...,
    *,
    permissions: list[str] | None = ...,
) -> Callable[[Callable[..., RetType]], Callable[..., RetType]]: ...


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
            callable_inj_context = CallableInjectionContext(injections)
            kwargs = inject_kwargs(injected_usecase_func, kwargs, callable_inj_context)

            func_code = usecase_func.__code__
            func_name = func_code.co_name

            actor = __check_actor(args, kwargs, func_code, type_hints)

            check_permissions(actor, permissions)

            callback_context = CallbackContext(
                success=True, actor=actor, fn_name=func_name
            )
            inj_context.injections[CallbackContext] = callback_context

            def run_callbacks():
                for callback in callbacks:
                    inj_callback = inject_function(callback, inj_context)
                    inj_callback(
                        **inject_kwargs(
                            callback,
                            {},
                            callable_inj_context,
                        )
                    )

            try:
                ret = validate_call(config={"arbitrary_types_allowed": True})(
                    injected_usecase_func
                )(*args, **kwargs)
                msg = "SUCCESS: '{}' called '{}'.".format(str(actor), func_name)
                logger.log(INFO, msg)
                run_callbacks()
                return ret
            except (UseCaseError, DomainError) as e:
                callback_context.success = False
                msg = "ERROR: '{}' called '{}' and '{}' happened.".format(
                    str(actor), func_name, str(e)
                )
                logger.log(WARNING, msg)
                run_callbacks()
                raise e

        return wrapper

    if func:
        # this happens when use_case is used like @use_case instead of @use_case()
        return decorator(func)

    return decorator
