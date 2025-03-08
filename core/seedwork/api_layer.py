import inspect
import json
import logging
from json import JSONDecodeError
from types import GenericAlias
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
    get_args,
)

from django.conf import settings
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    JsonResponse,
    RawPostDataException,
)
from django.urls import path
from django.utils.module_loading import import_string
from pydantic import BaseModel, ValidationError, create_model

from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import UseCaseError, UseCaseInputError

api_logger = logging.getLogger("api")


class RFC7807(BaseModel):
    err_type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    internal: Optional[Any] = None
    general_errors: Optional[list[str]] = None
    param_errors: Optional[dict[str, list[str]]] = None


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
        param_errors: Optional[dict[str, list[str]]] = None,
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
        super().__init__(data=error.model_dump(), status=error.status)


class ApiValidationError(Exception):
    def __init__(self, validation_error: ValidationError):
        self.validation_error = validation_error

    def to_error_response(self) -> ErrorResponse:
        field_errors: Dict[str, List[str]] = {}
        for error in self.validation_error.errors():
            # if len(error["loc"]) == 2:
            name = str(error["loc"][-1])
            if name in field_errors:
                field_errors[name].append(error["msg"])
            else:
                field_errors[name] = [error["msg"]]

        return ErrorResponse(
            param_errors=field_errors,
            general_errors=[],
            status=422,
            err_type="RequestValidationError",
            title="Malformed Request",
            internal={},  # validation_error.errors(include_context=False),
        )


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


def get_data_from_request(request: HttpRequest) -> dict[str, Any]:
    data: dict[str, Any] = {}
    # query params
    get_dict = request.GET.dict()
    data.update(get_dict)
    # files
    for key in request.FILES.dict():
        values = request.FILES.getlist(key)
        for v in values:
            if v.size and v.size > 50000000:
                raise ApiError("File size is too big. Max file size is 50MB.")
        if len(values) == 1:
            data[key] = values[0]
        else:
            data[key] = values
    # request resolver
    if request.resolver_match is not None:
        data.update(request.resolver_match.kwargs)
    # body
    try:
        body_str = request.body.decode("utf-8")
        body_dict = json.loads(body_str)
        data.update(body_dict)
    except (JSONDecodeError, RawPostDataException):
        for key, value in request.POST.dict().items():
            val: Any = value
            if "||EMPTYARRAY||" in val:
                val = []
            elif "||ARRAY||" in val and isinstance(val, str):
                v1 = val.replace("||ARRAY||", "")
                v2 = v1.split("||ARRAYSEPERATOR||")
                val = v2
            elif "||JSON||" in val and isinstance(val, str):
                v1 = val.replace("||JSON||", "")
                v2 = json.loads(v1)
                val = v2
            elif "||NULL||" == val:
                val = None
            data[key] = val
    # return
    return data


def _validate(request: HttpRequest, schema: Type[BaseModel]) -> BaseModel:
    data = get_data_from_request(request)
    return schema(root=data)


def catch_error(func: Callable[..., HttpResponse | FileResponse]):
    def catch(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ApiValidationError as e:
            return e.to_error_response()

        except ApiError as e:
            return ErrorResponse(
                param_errors=e.param_errors,
                title=e.title,
                detail=e.message,
                status=e.status,
                err_type="ApiError",
            )

        # except ObjectDoesNotExist as e:
        #     return ErrorResponse(
        #         title="404", status=404, err_type="NotFoundError", internal=str(e)
        #     )

        except UseCaseInputError as e:
            return ErrorResponse(
                title=e.message or "Input Error",
                param_errors=e.param_errors,
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


def get_return_type_of_function(func: Callable[..., Any]) -> Any:
    s = inspect.signature(func)
    if s.return_annotation == inspect.Parameter.empty:
        raise TypeError(
            "The function '{}' is missing a return type annotation.".format(
                func.__code__.co_name
            )
        )
    return s.return_annotation


def build_kwargs_for_api_function_from_request(
    s: inspect.Signature, request: HttpRequest, injectors_by_return_type: dict
):
    func_kwargs: dict[str, Any] = {}

    for parameter in s.parameters.values():
        annotation = parameter.annotation
        if annotation in injectors_by_return_type:
            inject_function = injectors_by_return_type[annotation]
            func_kwargs[parameter.name] = inject_function(request)

    if "data" in s.parameters:
        data_parameter = s.parameters["data"]
        try:
            model = create_model(
                "Input",
                root=(data_parameter.annotation, ...),
            )
            data = _validate(request, model)
        except ValidationError as e:
            raise ApiValidationError(e)

        func_kwargs["data"] = data.root  # type: ignore

    return func_kwargs


def build_response(
    result: Any, output_schema: Optional[Type]
) -> HttpResponse | FileResponse:
    if (
        output_schema
        and (
            HttpResponse in get_args(output_schema)
            or FileResponse in get_args(output_schema)
            or output_schema == FileResponse
            or output_schema == HttpResponse
        )
        and isinstance(result, output_schema)
    ):
        return result

    if output_schema:
        model = create_model(
            "Output",
            root=(output_schema, ...),
        )
        output_data = model(root=result)
        return JsonResponse(output_data.model_dump()["root"], safe=False)

    return JsonResponse({})


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
    def __get_injectors_by_return_type(cls):
        ret = {}
        for injector in cls._injectors:
            return_annotation = get_return_type_of_function(injector)
            ret[return_annotation] = injector
        return ret

    @staticmethod
    def generate_view_func(
        method_route: Dict,
    ) -> Callable[..., JsonResponse | FileResponse]:
        def decorator(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            if request.method in method_route:
                return method_route[request.method]["view"](request, *args, **kwargs)
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
        output_schema: Optional[Type] = None,
    ) -> Callable:
        s = inspect.signature(func)

        # error handling
        for p in s.parameters.values():
            a = p.annotation
            if a in cls._injectors_by_return_type and p.name == "data":
                raise TypeError(
                    "It is not allowed that the 'data' variable has the same type hint as "
                    "one of the injectors has as return type. "
                    "'data' is populated by the api with the submitted data."
                )
            if p.name == "data" and not (
                isinstance(a, GenericAlias) or issubclass(a, BaseModel)
            ):
                raise TypeError(
                    "The variable named 'data' must be typed with a pydantic model, or 'list' or 'dict'."
                )

        def wrapper(
            request: HttpRequest, *args, **kwargs
        ) -> HttpResponse | FileResponse:
            func_kwargs = build_kwargs_for_api_function_from_request(
                s, request, cls._injectors_by_return_type
            )
            result = func(**func_kwargs)
            response = build_response(result, output_schema)
            return response

        return catch_error(wrapper)

    def get(
        self,
        url: str = "",
        output_schema: Any = None,
    ):
        return self.api(url, "GET", output_schema)

    def post(
        self,
        url: str = "",
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "POST", output_schema)

    def put(
        self,
        url: str = "",
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "PUT", output_schema)

    def delete(
        self,
        url: str = "",
        output_schema: Optional[Type] = None,
    ):
        return self.api(url, "DELETE", output_schema)

    def api(
        self,
        url: str = "",
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        output_schema: Optional[Type] = None,
    ):
        def decorator(func: Callable[..., Union[Any, None]]):
            view = Router.generate_view(func, output_schema)
            self.__routes.append({"url": url, "method": method, "view": view})

        return decorator
