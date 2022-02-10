from rest_framework.response import Response
from rest_framework.request import Request
from apps.api.models import LoggedPath


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        # get the response
        response: Response = self.get_response(request)

        # set the data
        data = {
            'user': request.user if request.user.is_authenticated else None,
            'path': request.path,
            'status': response.status_code,
            'method': request.method
        }
        if response.status_code == 500 and request.method == 'POST':
            data.update({'data': request.data})

        # create the logged path
        LoggedPath.objects.create(**data)

        # return the response
        return response
