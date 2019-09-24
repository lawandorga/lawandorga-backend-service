#  rlcapp - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.api.errors import CustomError
from backend.static.emails import EmailSender
from backend.static.env_getter import get_website_base_url
from backend.static.error_codes import *
from ..models import UserProfile, ForgotPasswordLinks
from ..serializers import ForgotPasswordSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ForgotPasswordViewSet(ModelViewSet):
    queryset = ForgotPasswordLinks.objects.all()
    serializer_class = ForgotPasswordSerializer


class ForgotPasswordUnauthenticatedViewSet(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        if 'email' in request.data:
            email = request.data['email']
        else:
            raise CustomError(ERROR__API__EMAIL__NO_EMAIL_PROVIDED)
        try:
            user = UserProfile.objects.get(email=email)
        except:
            raise CustomError(ERROR__API__EMAIL__NO_EMAIL_PROVIDED)

        link_already = ForgotPasswordLinks.objects.filter(user=user).__len__()
        if link_already >= 1:
            raise CustomError(ERROR__API__USER__ALREADY_FORGOT_PASSWORD)

        user.is_active = False
        user.save()
        ip = get_client_ip(request)
        forgot_password_link = ForgotPasswordLinks(user=user, ip_address=ip)
        forgot_password_link.save()

        url = get_website_base_url() + "api/reset-password/" + forgot_password_link.link
        EmailSender.send_email_notification([user.email], "Password reset",
                                            "Your password was resetted click here: " + url)

        return Response()


class ResetPasswordViewSet(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, id):
        try:
            link = ForgotPasswordLinks.objects.get(link=id)
        except:
            raise CustomError(ERROR__API__USER__PASSWORD_RESET_LINK_DOES_NOT_EXIST)
        if 'new_password' not in request.data:
            raise CustomError(ERROR__API__USER__NEW_PASSWORD_NOT_PROVIDED)
        new_password = request.data['new_password']
        link.user.set_password(new_password)
        link.user.is_active = True
        link.user.save()
        link.delete()
        return Response()
