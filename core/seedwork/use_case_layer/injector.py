from typing import Any, Callable, TypeVar, get_type_hints

RT = TypeVar("RT")

R = TypeVar("R")
Injections = dict[type[R], R | Callable[..., R]]
_InjectionsDirect = dict[type[R], R]
_InjectionsCallable = dict[type[R], Callable[..., R]]


class InjectionContext:
    def __init__(self, injections: Injections) -> None:
        self.injections: _InjectionsDirect = {
            k: v for k, v in injections.items() if not callable(v)
        }
        self.callable_injections: _InjectionsCallable = {
            k: v for k, v in injections.items() if callable(v)
        }
        self.injections[InjectionContext] = self
        self.resolved_callable_injections: _InjectionsDirect = {}

    def has(self, injection) -> bool:
        if injection in self.injections:
            return True
        if injection in self.callable_injections:
            return True
        return False

    def get(self, injection: type[R]) -> R:
        if injection in self.injections:
            return self.injections[injection]
        if injection in self.resolved_callable_injections:
            return self.resolved_callable_injections[injection]
        if injection in self.callable_injections:
            func = self.callable_injections[injection]
            kwargs = inject_kwargs(func, {}, self)
            resolved: R = func(**kwargs)
            self.resolved_callable_injections[injection] = resolved
            return resolved
        raise ValueError(f"no injection found for type '{injection}'")

    def reset(self) -> None:
        """
        Resets the resolved callable injections.
        Call this method before each use case execution to ensure that
        callable injections are re-evaluated.
        This means that each callable injection will be request bound.
        Or more specifically usecase bound.
        """
        self.resolved_callable_injections = {}


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


def convert_args_to_kwargs(
    func: Callable[..., RT], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    func_code = func.__code__
    for index, value in enumerate(args):
        param_name = func_code.co_varnames[index]
        if param_name not in kwargs:
            kwargs[param_name] = value
    return kwargs
