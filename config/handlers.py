from django.http import JsonResponse
from apps.static.api_layer import RFC7807


def handler400(request, exception, template_name="404.html"):
    error = RFC7807(type='DjangoBadRequest', title='Bad Request', status=400)
    return JsonResponse(error.dict())


def handler403(request, exception, template_name="404.html"):
    error = RFC7807(type='DjangoForbidden', title='Forbidden', status=403)
    return JsonResponse(error.dict())


def handler404(request, exception, template_name="404.html"):
    error = RFC7807(type='DjangoNotFound', title='Not Found', status=404)
    return JsonResponse(error.dict())


def handler500(request, template_name="404.html"):
    error = RFC7807(type='DjangoServerError', title='Server Error', status=500)
    return JsonResponse(error.dict())
