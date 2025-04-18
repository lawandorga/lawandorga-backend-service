from functools import partial
from typing import Any, Callable, TypeVar, get_type_hints

RT = TypeVar("RT")

R = TypeVar("R")
Injections = dict[type[R], R | Callable[[], R]]


class InjectionContext:
    def __init__(self, injections: Injections) -> None:
        self.injections = {k: v for k, v in injections.items() if not callable(v)}
        self.injections[InjectionContext] = self

    def has(self, injection) -> bool:
        return injection in self.injections

    def get(self, injection: type[R]) -> R:
        return self.injections[injection]


class CallableInjectionContext(InjectionContext):
    def __init__(self, injections: Injections) -> None:
        self.injections = {k: v() for k, v in injections.items() if callable(v)}


def inject_function(
    func: Callable[..., RT], context: InjectionContext
) -> Callable[..., RT]:
    hints = get_type_hints(func)
    hints.pop("return", None)

    for name, hint in hints.items():
        if context.has(hint):
            func = partial(func, **{name: context.get(hint)})

    return func


def inject_kwargs(
    func: Callable[..., RT], kwargs: dict[str, Any], context: InjectionContext
) -> dict[str, Any]:
    hints = get_type_hints(func)
    hints.pop("return", None)

    for name, hint in hints.items():
        if context.has(hint) and name not in kwargs:
            kwargs[name] = context.get(hint)
        else:
            continue

    return kwargs
