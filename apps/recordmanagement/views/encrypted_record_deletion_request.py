from apps.recordmanagement.models.encrypted_record_deletion_request import EncryptedRecordDeletionRequest
from apps.recordmanagement.serializers import DeletionRequestListSerializer, DeletionRequestCreateSerializer
from apps.api.models.notification import Notification
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from apps.recordmanagement import serializers
from rest_framework.views import APIView
from django.db.models import QuerySet, Q
from apps.api.errors import CustomError
from rest_framework import viewsets
from django.utils import timezone
from apps.static import error_codes, permissions


class EncryptedRecordDeletionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DeletionRequestListSerializer
    queryset = EncryptedRecordDeletionRequest.objects.none()

    def get_serializer_class(self):
        if self.action in ['create']:
            return DeletionRequestCreateSerializer
        return self.get_serializer_class()

    def get_queryset(self) -> QuerySet:
        return EncryptedRecordDeletionRequest.objects.filter(
            Q(request_from__rlc=self.request.user.rlc) |
            Q(record__from_rlc=self.request.user.rlc)
        )

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)


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
            record_deletion_request = EncryptedRecordDeletionRequest.objects.get(
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
        record_deletion_request.processed_on = timezone.now()

        if action == "accept":
            # if record_deletion_request.state == "re":
            record_deletion_request.state = "gr"
            record_deletion_request.request_processed = request.user
            record_deletion_request.save()

            other_deletion_requests_of_same_record: [
                EncryptedRecordDeletionRequest
            ] = EncryptedRecordDeletionRequest.objects.filter(
                record=record_deletion_request.record, state="re"
            )
            for other_request in other_deletion_requests_of_same_record:
                other_request.state = "gr"
                other_request.request_processed = request.user
                other_request.save()

            Notification.objects.notify_record_deletion_accepted(
                request.user, record_deletion_request
            )
            record_deletion_request.record.delete()
        else:
            record_deletion_request.state = "de"
            record_deletion_request.save()

            Notification.objects.notify_record_deletion_declined(
                request.user, record_deletion_request
            )

        response_request = EncryptedRecordDeletionRequest.objects.get(
            pk=record_deletion_request.id
        )
        return Response(
            serializers.DeletionRequestListSerializer(response_request).data
        )
