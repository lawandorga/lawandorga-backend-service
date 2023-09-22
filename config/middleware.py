import json

from django.db.transaction import TransactionManagementError
from django.template.response import TemplateResponse
from django.utils.decorators import sync_only_middleware

from core.models import LoggedPath

__all__ = [
    "custom_debug_toolbar_middleware",
    "logging_middleware",
]


@sync_only_middleware
def custom_debug_toolbar_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        if "debug" in request.GET and response["content-type"] == "application/json":
            content = json.dumps(json.loads(response.content), sort_keys=True, indent=2)
            new_response = TemplateResponse(
                request, "api_debug.html", context={"content": content}
            ).render()
            return new_response

        return response

    return middleware


@sync_only_middleware
def logging_middleware(get_response):
    def create_data(request, response):
        data = {
            "user": request.user if request.user.is_authenticated else None,
            "path": request.get_full_path()[:200],
            "status": response.status_code if response.status_code else 0,
            "method": request.method if request.method else "UNKNOWN",
        }
        return data

    def middleware(request):
        response = get_response(request)
        data = create_data(request, response)
        try:
            LoggedPath.objects.create(**data)
        except TransactionManagementError:
            # happens if an error happens in an atomic block
            pass
        return response

    return middleware
