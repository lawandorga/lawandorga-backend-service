from django.http import JsonResponse

from core.seedwork.api_layer import RFC7807


def handler400(request, exception, template_name=""):
    error = RFC7807(
        err_type="DjangoBadRequest",
        title="Bad Request",
        status=400,
        internal=str(exception),
    )
    return JsonResponse(error.dict(), status=400)


def handler403(request, exception, template_name=""):
    error = RFC7807(
        err_type="DjangoForbidden",
        title="Forbidden",
        status=403,
        internal=str(exception),
    )
    return JsonResponse(error.dict(), status=403)


def handler404(request, exception, template_name=""):
    error = RFC7807(
        err_type="DjangoNotFound",
        title="Not Found",
        status=404,
        internal=str(exception)[:10],
    )
    return JsonResponse(error.dict(), status=404)


def handler500(request, template_name=""):
    error = RFC7807(err_type="DjangoServerError", title="Server Error", status=500)
    return JsonResponse(error.dict(), status=500)


def handler_csrf_error(request, reason=""):
    error = RFC7807(
        err_type="DjangoCsrfTokenError",
        title=(
            "Csrf Cookie Missing - Please make sure your browser "
            "does not block any cookies from Law&Orga"
        ),
        status=400,
        detail=(
            "Please make sure your browser does not block " "any cookies from Law&Orga."
        ),
        internal=reason,
    )
    return JsonResponse(error.dict(), status=400)
