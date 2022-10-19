from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from apps.core.models import LoggedPath


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get the response
        response = self.get_response(request)

        # set the data
        data = {
            "user": request.user if request.user.is_authenticated else None,
            "path": request.get_full_path()[:200],
            "status": response.status_code if response.status_code else 0,
            "method": request.method if request.method else "UNKNOWN",
        }

        # create the logged path
        LoggedPath.objects.create(**data)

        # return the response
        return response


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
