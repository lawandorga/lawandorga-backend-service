import asyncio
import inspect
import json
from datetime import datetime
from json import JSONDecodeError
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)

import pytz
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse, HttpRequest, JsonResponse, RawPostDataException
from django.urls import path
from django.utils.module_loading import import_string
from django.utils.timezone import localtime, make_aware
from pydantic import BaseModel, ValidationError, create_model, validator

from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import UseCaseError, UseCaseInputError


def __qs_to_list_validator(qs) -> List:
    if hasattr(qs, "all"):
        return list(qs.all())
    if isinstance(qs, list):
        return qs
    raise ValueError("The value is not a queryset or a list.")


def qs_to_list(x):
    return validator(x, pre=True, allow_reuse=True)(__qs_to_list_validator)


def __format_datetime_validator(v: datetime) -> str:
    datetime_format = "%Y-%m-%dT%H:%M:%S"
    if v.utcoffset() is None:
        return v.strftime(datetime_format)
    return localtime(v).strftime(datetime_format)


def format_datetime(x):
    return validator(x, allow_reuse=True)(__format_datetime_validator)


def __make_datetime_aware_validator(v: datetime) -> datetime:
    if v.utcoffset() is None:
        return make_aware(v, pytz.timezone("Europe/Berlin"))
    return v


def make_datetime_aware(x):
    return validator(x, allow_reuse=True)(__make_datetime_aware_validator)


class ApiError(Exception):
    param_errors: dict | None

    def __init__(
        self, message: dict | str, detail: str | None = None, status: int | None = None
    ):
        if isinstance(message, dict):
            self.param_errors = message
            self.message = "An input error happened."
            self.status = status if status else 422
        else:
            self.param_errors = None
            self.message = message
            self.status = status if status else 400
        self.title: str = self.message
        self.detail: None | str = detail if detail else None


class RFC7807(BaseModel):
    err_type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    internal: Optional[Any] = None
    general_errors: Optional[list[str]] = None
    param_errors: Optional[Dict[str, List[str]]] = None


def _validation_error_handler(validation_error: ValidationError) -> RFC7807:
    field_errors: Dict[str, List[str]] = {}
    for error in validation_error.errors():
        if len(error["loc"]) == 2:
            name = str(error["loc"][1])
            if name in field_errors:
                field_errors[name].append(error["msg"])
            else:
                field_errors[name] = [error["msg"]]

    return RFC7807(
        param_errors=field_errors,
        general_errors=[],
        status=422,
        err_type="RequestValidationError",
        title="Malformed Request",
        internal=validation_error.errors(),
    )


def _validate(request: HttpRequest, schema: Type[BaseModel]) -> BaseModel:
    data: Dict[str, Any] = {}
    # query params
    get_dict = request.GET.dict()
    data.update(get_dict)
    file = request.FILES.get("file", None)
    if file:
        data["file"] = file
    files = request.FILES.getlist("files", None)
    if files:
        data["files"] = files
    # request resolver
    if request.resolver_match is not None:
        data.update(request.resolver_match.kwargs)
    # body
    try:
        body_str = request.body.decode("utf-8")
        body_dict = json.loads(body_str)
        data.update(body_dict)
    except (JSONDecodeError, RawPostDataException):
        data.update(request.POST.dict())
    # validate
    return schema(root=data)


def _catch_error(func: Callable[..., Awaitable[JsonResponse | FileResponse]]):
    async def catch(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except ApiError as e:
            return ErrorResponse(
                param_errors=e.param_errors,
                title=e.title,
                detail=e.message,
                status=e.status,
                err_type="ApiError",
            )

        except ObjectDoesNotExist as e:
            return ErrorResponse(
                title="404", status=404, err_type="NotFoundError", internal=str(e)
            )

        except UseCaseInputError as e:
            return ErrorResponse(
                title=e.message,
                status=400,
                err_type="UseCaseInputError",
            )

        except UseCaseError as e:
            return ErrorResponse(
                title=e.message,
                status=400,
                err_type="UseCaseError",
            )

        except DomainError as e:
            return ErrorResponse(
                title=e.message,
                status=400,
                err_type="DomainError",
            )

    return catch


class ErrorResponse(JsonResponse):
    def __init__(
        self,
        err_type: str,
        title: str,
        status: int,
        detail: Optional[str] = None,
        general_errors: Optional[list[str]] = None,
        instance: Optional[str] = None,
        internal: Optional[Any] = None,
        param_errors: Optional[Dict[str, List[str]]] = None,
    ):
        error = RFC7807(
            err_type=err_type,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            internal=internal,
            param_errors=param_errors,
            general_errors=general_errors,
        )
        super().__init__(data=error.dict(), status=error.status)


InjectT = TypeVar("InjectT", bound=Any)
InjectorF = Callable[[HttpRequest], InjectT]


class Router:
    _injectors: list[InjectorF]
    _injectors_by_return_type: dict

    def __init__(self):
        super().__init__()
        self.__routes = []
        if not hasattr(self.__class__, "_injectors"):
            self.__class__._injectors = [
                import_string(i) for i in settings.API_INJECTORS
            ]
            self.__class__._injectors_by_return_type = (
                self.__class__.__get_injectors_by_return_type()
            )

    @classmethod
    def __get_injectors_by_return_type(cls) -> dict[InjectT, InjectorF]:
        ret: dict[InjectT, InjectorF] = {}
        for injector in cls._injectors:
            s = inspect.signature(injector)
            if s.return_annotation is None:
                raise TypeError("Api injectors need a return type annotation.")
            ret[s.return_annotation] = injector
        return ret

    @staticmethod
    def generate_view_func(
        method_route: Dict,
    ) -> Callable[..., Awaitable[JsonResponse]]:
        async def decorator(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            if request.method in method_route:
                return await method_route[request.method]["view"](
                    request, *args, **kwargs
                )
            else:
                return ErrorResponse(
                    title="Method not allowed", status=405, err_type="MethodNotAllowed"
                )

        return decorator

    @property
    def urls(self):
        urls = {}

        for route in self.__routes:
            if route["url"] in urls:
                if route["method"] in urls[route["url"]]:
                    raise ValueError("The same url and method must not exist.")
                else:
                    urls[route["url"]][route["method"]] = route
            else:
                urls[route["url"]] = {route["method"]: route}

        ret = []
        for url, method_route in urls.items():
            view = Router.generate_view_func(method_route)
            ret.append(path(url, view))

        return ret

    @classmethod
    def generate_view(
        cls,
        func: Callable[..., Union[Union[Awaitable[Any], Any], None]],
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
    ) -> Callable:
        s = inspect.signature(func)

        # error handling
        for parameter in s.parameters.values():
            annotation = parameter.annotation
            if annotation in cls._injectors_by_return_type and parameter.name == "data":
                raise TypeError(
                    "It is not allowed to have have a variable named 'data' injected with the api injectors. "
                    "'data' is populated by the api with the submitted data."
                )
            # if parameter.name == 'data' and not issubclass(annotation, BaseModel):
            #     raise TypeError(
            #         "The variable named 'data' must be typed with a pydantic model or a subclass of Type."
            #     )

        async def wrapper(
            request: HttpRequest, *args, **kwargs
        ) -> JsonResponse | FileResponse:
            # set up input
            func_kwargs: Dict[str, Any] = {}
            func_input = func.__code__.co_varnames[: func.__code__.co_argcount]

            # handle injections
            for parameter in s.parameters.values():
                annotation = parameter.annotation
                if annotation in cls._injectors_by_return_type:
                    inject_function = cls._injectors_by_return_type[annotation]
                    func_kwargs[parameter.name] = await sync_to_async(inject_function)(
                        request
                    )

            # validate the input
            if input_schema:
                try:
                    model = create_model(
                        "Input",
                        root=(input_schema, ...),
                    )
                    data = _validate(request, model)
                except ValidationError as e:
                    return ErrorResponse(**_validation_error_handler(e).dict())

                if "data" in func_input:
                    func_kwargs["data"] = data.root  # type: ignore

            # different layer errors
            if asyncio.iscoroutinefunction(func):
                async_func: Callable[..., Awaitable[Any]] = func
            else:
                async_func: Callable[..., Awaitable[Any]] = sync_to_async(func)  # type: ignore
            result: Any = await async_func(**func_kwargs)

            # validate the output
            if (
                inspect.isclass(output_schema)
                and issubclass(output_schema, FileResponse)
                and isinstance(result, FileResponse)
            ):
                return result
            if output_schema:
                model = create_model(
                    "Output",
                    root=(output_schema, ...),
                )
                output_data = await sync_to_async(model)(root=result)
                return JsonResponse(output_data.dict()["root"], safe=False)

            # default
            return JsonResponse({})

        return _catch_error(wrapper)

    def get(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "GET", input_schema, output_schema)

    def post(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "POST", input_schema, output_schema)

    def put(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "PUT", input_schema, output_schema)

    def delete(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "DELETE", input_schema, output_schema)

    def api(
        self,
        url: str = "",
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
    ):
        def decorator(func: Callable[..., Union[Any, None]]):
            view = Router.generate_view(func, input_schema, output_schema)
            self.__routes.append({"url": url, "method": method, "view": view})

        return decorator
