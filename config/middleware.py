import asyncio
import json

from django.http import HttpResponse
from django.utils.decorators import sync_and_async_middleware
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from core.models import LoggedPath

__all__ = [
    "custom_debug_toolbar_middleware",
    "logging_middleware",
    "TokenAuthenticationMiddleware",
]


@sync_and_async_middleware
def custom_debug_toolbar_middleware(get_response):
    def create_response(request, response):
        if "debug" in request.GET and response["content-type"] == "application/json":
            content = json.dumps(json.loads(response.content), sort_keys=True, indent=2)
            new_response = HttpResponse(
                "<html><body><pre>{}</pre></body></html>".format(content)
            )
            return new_response
        return response

    if asyncio.iscoroutinefunction(get_response):

        async def middleware(request):
            response = await get_response(request)
            response = create_response(request, response)
            return response

    else:

        def middleware(request):
            response = get_response(request)
            response = create_response(request, response)
            return response

    return middleware


@sync_and_async_middleware
def logging_middleware(get_response):
    def create_data(request, response):
        data = {
            "user": request.user if request.user.is_authenticated else None,
            "path": request.get_full_path()[:200],
            "status": response.status_code if response.status_code else 0,
            "method": request.method if request.method else "UNKNOWN",
        }
        return data

    if asyncio.iscoroutinefunction(get_response):

        async def middleware(request):
            response = await get_response(request)
            data = create_data(request, response)
            await LoggedPath.objects.acreate(**data)
            return response

    else:

        def middleware(request):
            response = get_response(request)
            data = create_data(request, response)
            LoggedPath.objects.create(**data)
            return response

    return middleware


class TokenAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        authenticate = False
        if hasattr(request, "user") and getattr(request.user, "id", None) is None:
            authenticate = True
        if not hasattr(request, "user"):
            authenticate = True

        if authenticate:
            user = self.authenticate(request)
            if user:
                request.user = user[0]

    def authenticate(self, request):
        try:
            jwt_auth = JWTAuthentication()
            user = jwt_auth.authenticate(request)
        except AuthenticationFailed:
            user = None
        return user
