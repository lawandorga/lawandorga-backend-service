from django.http import JsonResponse

from core.seedwork.api_layer import RFC7807


def handler400(_, __, ___=""):
    error = RFC7807(err_type="DjangoBadRequest", title="Bad Request", status=400)
    return JsonResponse(error.dict(), status=400)


def handler403(_, __, ___=""):
    error = RFC7807(err_type="DjangoForbidden", title="Forbidden", status=403)
    return JsonResponse(error.dict(), status=403)


def handler404(_, __, ___=""):
    error = RFC7807(err_type="DjangoNotFound", title="Not Found", status=404)
    return JsonResponse(error.dict(), status=404)


def handler500(_, __=""):
    error = RFC7807(err_type="DjangoServerError", title="Server Error", status=500)
    return JsonResponse(error.dict(), status=500)
