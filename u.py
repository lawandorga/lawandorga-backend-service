# from typing import Any, Callable, Concatenate, Optional, ParamSpec, TypeVar
#
# from typing_extensions import reveal_type
#
# Param = ParamSpec("Param")
# RetType = TypeVar("RetType")
# X = TypeVar("X")
#
# OriginalFunc = Callable[Concatenate[X, str, Param], RetType]
#
#
# # DecoratedFunc = Callable[Concatenate[str, Param], RetType]
#
#
# def get_authenticated_user():
#     return "John"
#
#
# def inject_user() -> Callable[
#     [Callable[Concatenate[X, str, Param], RetType]],
#     Callable[Concatenate[X, Param], RetType],
# ]:
#     def decorator(
#         func: Callable[Concatenate[X, str, Param], RetType]
#     ) -> Callable[Concatenate[X, Param], RetType]:
#         def wrapper(*args, **kwargs) -> RetType:
#             user = get_authenticated_user()
#             if user is None:
#                 raise Exception("Don't!")
#             return func(*args, user, **kwargs)  # <- call signature modified
#
#         return wrapper
#
#     return decorator
#
#
# @inject_user()
# def foo(a: int, username: str) -> bool:
#     print(username)
#     return bool(a % 2)
#
#
# foo(2)  # Type check OK
# # foo("no!")  # Type check should fail
# reveal_type(foo)
#
# C = TypeVar("C", bound=Callable)
#
#
# def logger(function: C) -> C:
#     def decorator(*args, **kwargs):
#         print("Function called!")
#         return function(*args, **kwargs)
#
#     return decorator
#
#
# @logger
# def example(arg: int, other: str) -> tuple[int, str]:
#     return arg, other
#
#
# reveal_type(example)
#
# T = TypeVar("T")
# P = ParamSpec("P")
#
#
# def catch_exception(function: Callable[P, T]) -> Callable[P, Optional[T]]:
#     def decorator(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
#         try:
#             return function(*args, **kwargs)
#         except Exception:
#             return None
#
#     return decorator
#
#
# @catch_exception
# def div(arg: int) -> float:
#     return arg / arg
#
#
# reveal_type(div)
#
#
# @catch_exception
# def plus(arg: int, other: int) -> int:
#     return arg + other
#
#
# reveal_type(plus)
#
# P1 = ParamSpec("P1")
# R = TypeVar("R")
# P2 = ParamSpec("P2")
# R1 = TypeVar("R1")
#
#
# class Findable:
#     def __init__(self, func):
#         self.__func = func
#
#     def __call__(self, *args, **kwargs):
#         return self.__func(*args, **kwargs)
#
#
# def logger2(
#     function: Callable[Concatenate[Findable, P2], R]
# ) -> Callable[Concatenate[str, P2], R]:
#     def decorator(*args, **kwargs):
#         print("Function called!")
#         return function(*args, **kwargs)
#
#     return decorator
#
#
# @logger2
# def example2(arg: int, other=Findable(lambda: 45)) -> tuple[int, str]:
#     return arg, other
#
#
# reveal_type(example2)
