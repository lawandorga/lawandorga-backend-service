import asyncio
import json
from json import JSONDecodeError
from typing import Any, Awaitable, Callable, Dict, List, Literal, Optional, Type, Union

from asgiref.sync import sync_to_async
from django.http import HttpRequest, JsonResponse
from django.urls import path
from django.utils.timezone import localtime
from pydantic import BaseConfig, BaseModel, ValidationError, create_model, validator

from core.models import UserProfile
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import UseCaseError, UseCaseInputError


def qs_to_list_validator(qs) -> List:
    if hasattr(qs, "all"):
        return list(qs.all())
    raise ValueError("The value is not a queryset")


def qs_to_list(x):
    return validator(x, pre=True, allow_reuse=True)(qs_to_list_validator)


def format_datetime_validator(v) -> str:
    datetime_format = "%Y-%m-%dT%H:%M:%S"
    if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
        return v.strftime(datetime_format)
    return localtime(v).strftime(datetime_format)


def format_datetime(x):
    return validator(x, allow_reuse=True)(format_datetime_validator)


class ApiError(Exception):
    def __init__(self, message):
        self.message = message


class RFC7807(BaseModel):
    err_type: str
    title: str
    status: int
    detail: Optional[Any] = None
    instance: Optional[str] = None
    internal: Optional[Any] = None
    param_errors: Optional[Dict[str, List[str]]] = None


class Config(BaseConfig):
    orm_mode = True


def validation_error_handler(validation_error: ValidationError) -> RFC7807:
    field_errors: Dict[str, List[str]] = {}
    for error in validation_error.errors():
        if len(error["loc"]) == 2:
            name = str(error["loc"][1])
            if name in field_errors:
                field_errors[name].append(error["msg"])
            else:
                field_errors[name] = [error["msg"]]

    form_error = {"non_field_errors": [], "field_errors": field_errors}
    return RFC7807(
        detail=form_error,
        status=422,
        err_type="RequestValidationError",
        title="Malformed Request",
        internal=validation_error.errors(),
    )


def validate(request: HttpRequest, schema: Type[BaseModel]) -> BaseModel:
    data: Dict[str, Any] = {}
    # query params
    data.update(request.GET)
    # request resolver
    if request.resolver_match is not None:
        data.update(request.resolver_match.kwargs)
    # body
    body_str = request.body.decode("utf-8")
    try:
        body_dict = json.loads(body_str)
        data.update(body_dict)
    except JSONDecodeError:
        pass
    # validate
    return schema(root=data)


class ErrorResponse(JsonResponse):
    def __init__(
        self,
        err_type: str,
        title: str,
        status: int,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        internal: Optional[Any] = None,
        param_errors: Optional[Dict[str, List[str]]] = None,
    ):
        error = RFC7807(
            err_type=err_type,
            title=title,
            status=status,
            detail=detail or title,
            instance=instance,
            internal=internal,
            param_errors=param_errors,
        )
        super().__init__(data=error.dict(), status=error.status)


class Router:
    def __init__(self):
        self.__routes = []

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

    @staticmethod
    def generate_view(
        func: Callable[..., Union[Union[Awaitable[Any], Any], None]],
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ) -> Callable:
        async def wrapper(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            # set up input
            func_kwargs: Dict[str, Any] = {}
            func_input = func.__code__.co_varnames[: func.__code__.co_argcount]

            # handle auth
            is_authenticated = request.user.is_authenticated
            not_authenticated_error = ErrorResponse(
                err_type="NotAuthenticated",
                title="Login Required",
                detail="You need to be logged in.",
                status=401,
            )

            if is_authenticated:
                user: UserProfile = request.user  # type: ignore

            if "user" in func_input:
                if not is_authenticated:
                    return not_authenticated_error

                func_kwargs["user"] = user

            if "rlc_user" in func_input:
                if not is_authenticated:
                    return not_authenticated_error

                if not hasattr(request.user, "rlc_user"):
                    return ErrorResponse(
                        err_type="RoleRequired",
                        title="Org User Required",
                        detail="You need to have the rlc user role.",
                        status=403,
                    )

                func_kwargs["rlc_user"] = user.rlc_user

            if "private_key_user" in func_input:
                if not is_authenticated:
                    return not_authenticated_error

                func_kwargs["private_key_user"] = user.get_private_key(request=request)

            if "statistics_user" in func_input:
                if not is_authenticated:
                    return not_authenticated_error

                if not hasattr(request.user, "statistic_user"):
                    return ErrorResponse(
                        err_type="RoleRequired",
                        title="Statistics User Required",
                        detail="You need to have the statistics user role.",
                        status=403,
                    )

                func_kwargs["statistics_user"] = user.statistic_user

            # validate the input
            if input_schema:
                try:
                    model = create_model(
                        "Input",
                        root=(input_schema, ...),
                    )
                    data = validate(request, model)
                except ValidationError as e:
                    return ErrorResponse(**validation_error_handler(e).dict())

                if "data" in func_input:
                    func_kwargs["data"] = data.root  # type: ignore

            # different layer errors
            try:
                if asyncio.iscoroutinefunction(func):
                    async_func: Callable[..., Awaitable[Any]] = func
                else:
                    async_func: Callable[..., Awaitable[Any]] = sync_to_async(func)  # type: ignore
                result: Any = await async_func(**func_kwargs)
            except ApiError as e:
                return ErrorResponse(
                    title=e.message,
                    status=400,
                    err_type="ApiError",
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

            # validate the output
            if output_schema:
                model = create_model(
                    "Output",
                    root=(output_schema, ...),
                )
                try:
                    output_data = await sync_to_async(model)(root=result)
                except ValidationError as e:
                    return ErrorResponse(
                        err_type="OutputError",
                        title="Server Error",
                        internal=e.errors(),
                        status=500,
                    )
                return JsonResponse(output_data.dict()["root"], safe=False)

            # default
            return JsonResponse({})

        return wrapper

    def get(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "GET", input_schema, output_schema, auth, error_dict)

    def post(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "POST", input_schema, output_schema, auth, error_dict)

    def put(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "PUT", input_schema, output_schema, auth, error_dict)

    def delete(
        self,
        url: str = "",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "DELETE", input_schema, output_schema, auth, error_dict)

    def api(
        self,
        url: str = "",
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        input_schema: Optional[Type] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        def decorator(func: Callable[..., Union[Any, None]]):
            view = Router.generate_view(
                func, input_schema, output_schema, auth, error_dict
            )
            self.__routes.append({"url": url, "method": method, "view": view})

        return decorator
