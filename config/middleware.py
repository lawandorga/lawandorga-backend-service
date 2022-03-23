from django.core.exceptions import RequestDataTooBig
from apps.api.models import LoggedPath


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # save the body for 500 errors now because it will not be available after get_response
        try:
            body = request.body
        except RequestDataTooBig:
            body = b'LoggingMiddleware Exception: RequestDateTooBig'

        # get the response
        response = self.get_response(request)

        # set the data
        print(request.get_full_path())
        data = {
            'user': request.user if request.user.is_authenticated else None,
            'path': request.get_full_path(),
            'status': response.status_code if response.status_code else 0,
            'method': request.method if request.method else 'UNKNOWN'
        }
        if response.status_code == 500:
            data.update({'data': body.decode('utf-8')})

        # create the logged path
        LoggedPath.objects.create(**data)

        # return the response
        return response
