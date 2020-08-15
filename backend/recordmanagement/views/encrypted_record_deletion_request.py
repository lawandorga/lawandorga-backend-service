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
from backend.recordmanagement import models, serializers
from backend.static import error_codes, permissions
from backend.api.models import UserProfile, Notification


class EncryptedRecordDeletionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EncryptedRecordDeletionRequestSerializer
    queryset = models.EncryptedRecordDeletionRequest.objects.all()

    def list(self, request, *args, **kwargs):
        if (
            not request.user.has_permission(
                permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
                for_rlc=request.user.rlc,
            )
            and not request.user.is_superuser
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        if request.user.is_superuser:
            queryset = models.EncryptedRecordDeletionRequest.objects.all()
        else:
            queryset = models.EncryptedRecordDeletionRequest.objects.filter(
                request_from__rlc=request.user.rlc
            )
        return Response(
            serializers.EncryptedRecordDeletionRequestSerializer(
                queryset, many=True
            ).data
        )

    def create(self, request, **kwargs):
        if "record_id" not in request.data:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__ID_NOT_PROVIDED)

        record = models.EncryptedRecord.objects.get_record(
            request.user, request.data["record_id"]
        )
        if not record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        if (
            models.EncryptedRecordDeletionRequest.objects.filter(
                record=record, state="re", request_from=request.user
            ).count()
            >= 1
        ):
            raise CustomError(
                error_codes.ERROR__RECORD__RECORD_DELETION__ALREADY_REQUESTED
            )
        deletion_request = models.EncryptedRecordDeletionRequest(
            request_from=request.user, record=record,
        )
        if "explanation" in request.data:
            deletion_request.explanation = request.data["explanation"]
        deletion_request.save()

        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS],
            from_rlc=request.user.rlc,
            for_rlc=request.user.rlc,
        )
        for user in users_with_permissions:
            Notification.objects.create_notification_record_deletion_request_requested(
                user, request.user, record
            )

        return Response(
            serializers.EncryptedRecordDeletionRequestSerializer(deletion_request).data,
            status=201,
        )


class EncryptedRecordDeletionProcessViewSet(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.has_permission(
            permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS, for_rlc=user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if "request_id" not in request.data:
            raise CustomError(error_codes.ERROR__API__ID_NOT_PROVIDED)
        try:
            record_deletion_request = models.EncryptedRecordDeletionRequest.objects.get(
                pk=request.data["request_id"]
            )
        except:
            raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)
        if record_deletion_request.record.from_rlc != user.rlc:
            raise CustomError(error_codes.ERROR__API__WRONG_RLC)

        if record_deletion_request.state != "re":
            raise CustomError(error_codes.ERROR__API__ALREADY_PROCESSED)

        if "action" not in request.data:
            raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)
        action = request.data["action"]
        if action != "accept" and action != "decline":
            raise CustomError(error_codes.ERROR__API__ACTION_NOT_VALID)

        record_deletion_request.request_processed = user
        record_deletion_request.processed_on = datetime.utcnow().replace(
            tzinfo=pytz.utc
        )

        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS],
            from_rlc=request.user.rlc,
            for_rlc=request.user.rlc,
        )
        for current_user in users_with_permissions:
            if current_user != user:
                Notification.objects.create_notification_record_deletion_request_requested(
                    current_user, request.user, record_deletion_request.record
                )

        if action == "accept":
            # if record_deletion_request.state == "re":
            record_deletion_request.state = "gr"
            record_deletion_request.save()

            other_deletion_requests_of_same_record: [
                models.EncryptedRecordDeletionRequest
            ] = models.EncryptedRecordDeletionRequest.objects.filter(
                record=record_deletion_request.record, state="re"
            )
            for other_request in other_deletion_requests_of_same_record:
                other_request.state = "gr"
                other_request.save()

            record_deletion_request.record.delete()
        else:
            record_deletion_request.state = "de"
            record_deletion_request.save()

        response_request = models.EncryptedRecordDeletionRequest.objects.get(
            pk=record_deletion_request.id
        )
        return Response(
            serializers.EncryptedRecordDeletionRequestSerializer(response_request).data
        )
