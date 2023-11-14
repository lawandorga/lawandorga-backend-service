from functools import partial, wraps
from typing import Callable, ParamSpec, TypeVar, get_type_hints


def validate_this(user: str, num1: int, num2: float):
    return num1, num2


Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def wrapper(fn: Callable[..., RetType]) -> Callable[..., RetType]:
    p_fn = partial(fn, num2=12)
    p_fn.__annotations__ = fn.__annotations__

    @wraps(p_fn)
    def inner(*args, **kwargs):
        return p_fn(*args, **kwargs)

    return inner


w_fn = wrapper(validate_this)
hints = get_type_hints(w_fn)
