from rest_framework import status, serializers
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text


class EntryAlreadyExistingError(serializers.ValidationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = (
        "the entry which was tried to create, existed already in the database"
    )


class CustomError(APIException):
    status_code = 400
    default_code = "law_orga.custom_error"
    default_detail = "base error, should be specified"

    def __init__(self, detail):
        if isinstance(detail, dict):
            if "error_detail" in detail:
                self.detail = detail["error_detail"]
            if "error_code" in detail:
                self.default_code = detail["error_code"]
            if "error_status_code" in detail:
                self.status_code = detail["error_status_code"]
        elif detail is not None:
            self.detail = {"detail": force_text(detail)}
        else:
            self.detail = {"detail": force_text(self.default_detail)}
