from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from core.auth.models import UserProfile
from core.auth.use_cases.user import change_password_of_user
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@csrf_exempt
def command__logout(request):
    logout(request)

    return HttpResponse()


@router.post(url="change_password/", input_schema=schemas.InputPasswordChange)
def command__change_password(user: UserProfile, data: schemas.InputPasswordChange):
    change_password_of_user(user, data.current_password, data.new_password)
