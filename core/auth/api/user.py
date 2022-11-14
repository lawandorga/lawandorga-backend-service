import json
from json import JSONDecodeError

from django.conf import settings
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.auth.models import UserProfile
from core.seedwork.api_layer import ErrorResponse

from django.contrib.auth.views import LoginView


import re


def strip_scheme(url: str):
    return re.sub(r'^https?:\/\/', '', url)


class CustomLoginView(LoginView):
    redirect_url = settings.MAIN_FRONTEND_URL
    success_url_allowed_hosts = {strip_scheme(settings.MAIN_FRONTEND_URL),
                                 strip_scheme(settings.STATISTICS_FRONTEND_URL)}


@csrf_exempt
def command__login(request):
    error = ErrorResponse(
        param_errors={"general": ["The E-Mail or the password is wrong."]},
        status=422,
        err_type="ApiError",
        title="Wrong Combination",
    )

    # check user exists and password is correct
    try:
        body = json.loads(request.body)
        assert "email" in body and "password" in body
        user = UserProfile.objects.get(email=body["email"])
        assert user.check_password(body["password"])
    except (JSONDecodeError, AssertionError, ObjectDoesNotExist):
        return error

    # check if user active and user accepted in rlc
    if not user.rlc_user.email_confirmed:
        message = "You can not login, yet. Please confirm your email first."
        return JsonResponse({"non_field_errors": [message]}, status=400)

    if not user.rlc_user.is_active:
        message = (
            "You can not login. Your account was deactivated by one of your admins."
        )
        return JsonResponse({"non_field_errors": [message]}, status=400)

    if not user.rlc_user.accepted:
        message = "You can not login, yet. You need to be accepted as member by one of your admins."
        return JsonResponse({"non_field_errors": [message]}, status=400)

    # login
    login(request, user)

    # set private key
    if hasattr(user, "rlc_user"):
        request.session["private_key"] = user.rlc_user.get_private_key(
            password_user=body["password"]
        )

    # return
    return HttpResponse()


@csrf_exempt
def command__logout(request):
    logout(request)

    return HttpResponse()
