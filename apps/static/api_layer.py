from typing import Callable, Dict, List, Optional, Type

from django.http import HttpRequest, JsonResponse
from pydantic import BaseConfig, BaseModel, ValidationError, create_model

from apps.api.models import UserProfile
from apps.static.service_layer import ServiceResult
from django.views.decorators.csrf import csrf_exempt


class Config(BaseConfig):
    orm_mode = True


def validation_error_handler(validation_error: ValidationError):
    field_errors: Dict[str, List[str]] = {}
    for error in validation_error.errors():
        if len(error["loc"]) == 1:
            name = str(error["loc"][0])
            if name in field_errors:
                field_errors[name].append(error["msg"])
            else:
                field_errors[name] = [error["msg"]]

    form_error = {"non_field_errors": [], "field_errors": field_errors}
    return {"data": form_error, "context": validation_error.errors()}


def validate(request: HttpRequest, schema: Type[BaseModel]):
    data = {}
    data.update(request.POST)
    data.update(request.GET)
    data.update(request.resolver_match.kwargs)
    return schema(**data)


class ErrorResponse:
    def __init__(self, status=None, data=None):
        self.status = status
        self.data = {"data": data}
        assert self.data is not None and self.status is not None

    @property
    def value(self):
        return JsonResponse(self.data, status=self.status)


class API:
    @staticmethod
    def split(func) -> Callable[..., JsonResponse]:
        def decorator(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            split_obj: Dict[str, Dict[str, Callable[..., JsonResponse]]] = func()
            if request.method not in split_obj:
                return JsonResponse({"data": "Method not allowed."}, status=405)
            else:
                for key, action in split_obj[request.method].items():
                    if request.resolver_match.route.endswith(key):
                        result = action(request, *args, _allow=True, **kwargs)
                        return result
                return JsonResponse({"data": "Method not allowed."}, status=405)

        return csrf_exempt(decorator)

    @staticmethod
    def api(
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        def decorator(service_func) -> Callable[..., JsonResponse]:
            def wrapper(
                request: HttpRequest, *args, _allow=False, **kwargs
            ) -> JsonResponse:
                assert (
                    _allow
                ), "Do not use @API.api in urlpatterns directly, use @API.split instead."

                # set up input
                service_func_kwargs = {}
                service_func_input = service_func.__code__.co_varnames

                # handle auth
                if auth:
                    if not request.user.is_authenticated:
                        return JsonResponse(
                            {"data": "You need to be logged in."}, status=401
                        )

                    user: UserProfile = request.user  # type: ignore

                    if not hasattr(user, "rlc_user"):
                        return JsonResponse(
                            {"data": "You need to have the rlc user role."}, status=403
                        )

                    if "user" in service_func_input:
                        service_func_kwargs["user"] = user
                    if "private_key_user" in service_func_input:
                        service_func_kwargs["private_key_user"] = user.get_private_key(
                            request=request
                        )

                # validate the input
                if input_schema:
                    try:
                        data = validate(request, input_schema)
                    except ValidationError as e:
                        return JsonResponse(
                            validation_error_handler(e), status=422, safe=False
                        )

                    if "data" in service_func_input:
                        service_func_kwargs["data"] = data

                # service layer next step
                result: ServiceResult = service_func(**service_func_kwargs)

                # log service layer
                # if auth:
                #     log_message = result.message.format(request.user.email)
                # else:
                #     log_message = result.message
                # TODO: log

                # error handling
                if not result.success:
                    if error_dict and result.message in error_dict:
                        return error_dict[result.message].value
                    return JsonResponse({"detail": result.value}, status=400)

                # validate the output
                if output_schema:
                    model = create_model(
                        "Output",
                        root=(output_schema, ...),
                    )
                    output_data = model(root=result.value)
                    return JsonResponse(output_data.dict()["root"], safe=False)

                # default
                return JsonResponse({})

            return wrapper

        return decorator
