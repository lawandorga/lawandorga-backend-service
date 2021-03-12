#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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

from datetime import datetime

import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.api.models import UserEncryptionKeys, UserProfile, Notification
from backend.recordmanagement import models, serializers
from backend.static import error_codes, permissions
from backend.static.encryption import RSAEncryption
from backend.static.middleware import get_private_key_from_request


class RecordPermissionViewSet(viewsets.ModelViewSet):
    queryset = models.RecordPermission.objects.all()
    serializer_class = serializers.EncryptedRecordPermissionSerializer


class EncryptedRecordPermissionRequestViewSet(APIView):
    def post(self, request, id) -> Response:
        record: models.EncryptedRecord = models.EncryptedRecord.objects.get_record(
            request.user, id
        )
        if record.from_rlc != request.user.rlc:
            raise CustomError(error_codes.ERROR__API__WRONG_RLC)

        if record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__ALREADY_WORKING_ON)

        if (
            models.EncryptedRecordPermission.objects.filter(
                record=record, request_from=request.user, state="re"
            ).count()
            >= 1
        ):
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__ALREADY_REQUESTED)
        can_edit = False
        if "can_edit" in request.data:
            can_edit = request.data["can_edit"]

        record_permission = models.EncryptedRecordPermission(
            request_from=request.user, record=record, can_edit=can_edit
        )
        record_permission.save()

        Notification.objects.notify_record_permission_requested(
            request.user, record_permission
        )

        return Response(
            serializers.EncryptedRecordPermissionSerializer(record_permission).data
        )


class EncryptedRecordPermissionProcessViewSet(APIView):
    def get(self, request) -> Response:
        """
        used from admins to see which permission requests are for the own rlc in the system
        :param request:
        :return:
        """
        user = request.user
        if not user.has_permission(
            permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
            for_rlc=user.rlc,
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        requests = models.EncryptedRecordPermission.objects.filter(
            record__from_rlc=user.rlc
        )
        return Response(
            serializers.EncryptedRecordPermissionSerializer(requests, many=True).data
        )

    def post(self, request) -> Response:
        """
        used to admit or decline a given permission request
        :param request:
        :return:
        """
        user: UserProfile = request.user
        if not user.has_permission(
            permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
            for_rlc=user.rlc,
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        if "id" not in request.data:
            raise CustomError(error_codes.ERROR__API__ID_NOT_PROVIDED)
        try:
            permission_request: models.EncryptedRecordPermission = models.EncryptedRecordPermission.objects.get(
                pk=request.data["id"]
            )
        except Exception as e:
            raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)

        if permission_request.record.from_rlc != user.rlc:
            raise CustomError(error_codes.ERROR__API__WRONG_RLC)
        if "action" not in request.data:
            raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)
        action = request.data["action"]
        if action != "accept" and action != "decline":
            raise CustomError(error_codes.ERROR__API__ACTION_NOT_VALID)

        if permission_request.state != "re":
            raise CustomError(error_codes.ERROR__API__ALREADY_PROCESSED)

        if action == "accept":
            users_private_key = get_private_key_from_request(request)
            record_key = permission_request.record.get_decryption_key(
                user, users_private_key
            )
            users_public_key = permission_request.request_from.get_public_key()
            encrypted_record_key = RSAEncryption.encrypt(record_key, users_public_key)
            record_encryption = models.RecordEncryption(
                user=permission_request.request_from,
                record=permission_request.record,
                encrypted_key=encrypted_record_key,
            )
            record_encryption.save()

            permission_request.state = "gr"
            permission_request.save()

            Notification.objects.notify_record_permission_accepted(
                request.user, permission_request
            )
        else:
            permission_request.state = "de"
            permission_request.save()
            Notification.objects.notify_record_permission_declined(
                request.user, permission_request
            )
        permission_request.request_processed = user
        permission_request.processed_on = datetime.utcnow().replace(tzinfo=pytz.utc)

        return Response(
            serializers.EncryptedRecordPermissionSerializer(permission_request).data
        )
