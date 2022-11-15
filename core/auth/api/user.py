from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def command__logout(request):
    logout(request)

    return HttpResponse()
