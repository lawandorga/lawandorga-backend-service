from rest_framework.response import Response
from apps.api.models import LoggedPath


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get the response
        response: Response = self.get_response(request)

        # log which endpoint is called
        user = request.user
        if not request.user.is_authenticated:
            user = None
        LoggedPath.objects.create(user=user, path=request.path, status=response.status_code)

        # return the response
        return response
