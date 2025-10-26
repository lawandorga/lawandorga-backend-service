from typing import Any, Callable, TypeVar, get_type_hints

RT = TypeVar("RT")

R = TypeVar("R")
Injections = dict[type[R], R | Callable[[], R]]


class InjectionContext:
    def __init__(self, injections: Injections) -> None:
        self.injections = {k: v for k, v in injections.items() if not callable(v)}
        self.callable_injections = {k: v for k, v in injections.items() if callable(v)}
        self.injections[InjectionContext] = self

    def has(self, injection) -> bool:
        if injection in self.injections:
            return True
        if injection in self.callable_injections:
            return True
        return False

    def get(self, injection: type[R]) -> R:
        if injection in self.injections:
            return self.injections[injection]
        if injection in self.callable_injections:
            func = self.callable_injections[injection]
            kwargs = inject_kwargs(func, {}, self)
            return func(**kwargs)  # type: ignore
        assert False


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
