import inspect
from typing import Any

from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.utils.module_loading import import_string
from pydantic import ValidationError, validate_call

from core.auth.models.org_user import OrgUser
from core.seedwork.api_layer import (
    ApiError,
    ApiValidationError,
    ErrorResponse,
    Router,
    get_data_from_request,
    get_return_type_of_function,
)
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import UseCaseError, UseCaseInputError

router = Router()


USECASES = import_string(settings.USECASE_FUNCTIONS)


@router.post("")
def command(org_user: OrgUser, data: dict[str, Any]):
    action = data.pop("action", None)
    if action is None:
        raise ApiError("action is required")

    fn = USECASES.get(action, None)
    if fn is None:
        raise ApiError(f"unknown action: {action}")

    try:
        validate_call(config={"arbitrary_types_allowed": True})(fn)(org_user, **data)
    except ValidationError as e:
        raise ApiValidationError(e)


INJECTORS = [import_string(i) for i in settings.API_INJECTORS]
INJECTORS_BY_RETURN_TYPE = {get_return_type_of_function(f): f for f in INJECTORS}


def django_command(request: HttpRequest) -> HttpResponse:
    print(2)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = get_data_from_request(request)
    except ApiError as e:
        return ErrorResponse(
            param_errors=e.param_errors,
            title=e.title,
            detail=e.message,
            status=e.status,
            err_type="ApiError",
        )

    data.pop("action", None)
    action = request.GET.get("action", None)
    if action is None:
        return HttpResponseBadRequest("action is required")

    fn = USECASES.get(action, None)
    if fn is None:
        return HttpResponseNotFound(f"unknown action: {action}")

    s = inspect.signature(fn)
    p = s.parameters.get("__actor", None)
    if p is None:
        raise ValueError(f"__actor is required for {fn}")
    a = p.annotation
    if a not in INJECTORS_BY_RETURN_TYPE:
        raise ValueError(f"__actor type {a} is not supported for {fn}")
    try:
        actor = INJECTORS_BY_RETURN_TYPE[a](request)
    except ApiError as e:
        return ErrorResponse(
            param_errors=e.param_errors,
            title=e.title,
            detail=e.message,
            status=e.status,
            err_type="ApiError",
        )

    try:
        validate_call(config={"arbitrary_types_allowed": True})(fn)(actor, **data)

    except ValidationError as e:
        return ApiValidationError(e).to_error_response()

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

    return HttpResponse()
