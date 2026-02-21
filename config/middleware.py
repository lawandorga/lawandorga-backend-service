import json

from django.template.response import TemplateResponse
from django.utils.decorators import sync_only_middleware

__all__ = [
    "custom_debug_toolbar_middleware",
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
