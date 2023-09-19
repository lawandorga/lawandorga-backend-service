from typing import Any

from django.conf import settings
from django.utils.module_loading import import_string
from pydantic import ValidationError, validate_call

from core.auth.models.org_user import RlcUser
from core.seedwork.api_layer import ApiError, ApiValidationError, Router

router = Router()


USECASES = import_string(settings.USECASE_FUNCTIONS)


@router.post("")
def command(rlc_user: RlcUser, data: dict[str, Any]):
    action = data.pop("action", None)
    if action is None:
        raise ApiError("action is required")

    fn = USECASES.get(action, None)
    if fn is None:
        raise ApiError(f"unknown action: {action}")

    try:
        validate_call(config={"arbitrary_types_allowed": True})(fn)(rlc_user, **data)
    except ValidationError as e:
        raise ApiValidationError(e)
