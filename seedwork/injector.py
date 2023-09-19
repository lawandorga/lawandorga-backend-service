from functools import partial
from typing import Callable, TypeVar, get_type_hints

RT = TypeVar("RT")

R = TypeVar("R")
Injections = dict[type[R], R]


class InjectionContext:
    def __init__(self, injections: Injections) -> None:
        self.injections = injections

    def has(self, injection) -> bool:
        return injection in self.injections

    def get(self, injection: type[R]) -> R:
        return self.injections[injection]


def inject_function(
    func: Callable[..., RT], context: InjectionContext
) -> Callable[..., RT]:
    hints = get_type_hints(func)
    hints.pop("return", None)

    for name, hint in hints.items():
        if name == "context":
            func = partial(func, context=context)
        elif context.has(hint):
            func = partial(func, **{name: context.get(hint)})
        else:
            continue

    return func
