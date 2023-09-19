import inspect
from functools import partial, wraps
from typing import Callable, ParamSpec, TypeVar, get_type_hints

from pydantic import validate_call


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

print("hin", hints)
print("wfn", w_fn(2, 3))
print("sig", inspect.signature(w_fn).parameters)
print("val", validate_call(w_fn)("mr. x", 3))
