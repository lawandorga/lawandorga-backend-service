# import inspect
# from typing import Callable, Any, ForwardRef
#
# from pydantic.typing import evaluate_forwardref
#
#
# class Injection:
#     def __init__(self, call):
#         self.call = call
#
#
# def Depends(x):
#     print(x)
#     return Injection(x)
#
#
# def wrap(func):
#     def new_func(*args, **kwargs):
#         func(*args, **kwargs)
#
#     return new_func
#
#
# # @wrap
# def a_plus_b(a, b=Depends(8)):
#     return a + b
#
#
# def get_typed_annotation(annotation: Any, globalns: dict[str, Any]) -> Any:
#     if isinstance(annotation, str):
#         annotation = ForwardRef(annotation)
#         annotation = evaluate_forwardref(annotation, globalns, globalns)
#     return annotation
#
#
# def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
#     signature = inspect.signature(call)
#     globalns = getattr(call, "__globals__", {})
#     typed_params = [
#         inspect.Parameter(
#             name=param.name,
#             kind=param.kind,
#             default=param.default,
#             annotation=get_typed_annotation(param.annotation, globalns),
#         )
#         for param in signature.parameters.values()
#     ]
#     typed_signature = inspect.Signature(typed_params)
#     return typed_signature
#
#
# print(get_typed_signature(a_plus_b).parameters.items())
#
#
# a_plus_b(**{'a': 1, 'b': 2, 'c': 3})
