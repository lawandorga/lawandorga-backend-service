from apps.recordmanagement.models.record import Record, RecordEncryptionNew
from apps.recordmanagement.serializers import PoolConsultantSerializer, PoolRecordSerializer
from apps.recordmanagement.models.pool import PoolConsultant, PoolRecord
from rest_framework.decorators import action
from apps.static.permissions import PERMISSION_CAN_CONSULT
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.api.errors import CustomError
from rest_framework import viewsets, status, mixins
from apps.static import error_codes


class PoolConsultantViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = PoolConsultant.objects.none()
    serializer_class = PoolConsultantSerializer

    def create(self, request, *args, **kwargs):
        # check permissions (can consult)
        user = request.user
        if not user.has_permission(PERMISSION_CAN_CONSULT, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if PoolRecord.objects.filter(record__template__rlc=user.rlc).count() >= 1:
            entry = PoolRecord.objects.filter(record__template__rlc=user.rlc).first()
            record = entry.record
            record.save()

            if not RecordEncryptionNew.objects.filter(user=user, record=record).exists():
                new_keys = RecordEncryptionNew(user=user, record=record, encrypted_key=entry.record_key)
                new_keys.encrypt(user.get_public_key())
                new_keys.save()

            entry.delete()
            return Response({"action": "matched"})
        else:
            pool_consultant = PoolConsultant(consultant=user)
            pool_consultant.save()

            number_of_entries = PoolConsultant.objects.filter(consultant=user).count()
            return_val = PoolConsultantSerializer(pool_consultant).data
            return_val.update(
                {"action": "created", "number_of_enlistings": number_of_entries}
            )
            return Response(return_val)


class PoolRecordViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = PoolRecord.objects.none()
    serializer_class = PoolRecordSerializer

    def create(self, request, *args, **kwargs):
        record = get_object_or_404(Record.objects.filter(template__rlc=request.user.rlc), pk=request.data['record'])

        if PoolRecord.objects.filter(record=record).exists():
            data = {'non_field_errors': ['This record is already in the record pool.']}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not RecordEncryptionNew.objects.filter(record=record, user=request.user).exists():
            data = {'non_field_errors': ['You need to have access to this record in order to be able to yield it.']}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        private_key = request.user.get_private_key(request=request)
        record_decryption_key = record.get_aes_key(user=request.user, private_key_user=private_key)

        if PoolConsultant.objects.filter(consultant__rlc=request.user.rlc).count() >= 1:
            entry = PoolConsultant.objects.filter(consultant__rlc=request.user.rlc).order_by("created").first()
            new_consultant = entry.consultant
            entry.delete()

            # RecordEncryptionNew.objects.filter(record=record, user=request.user).delete()
            if not RecordEncryptionNew.objects.filter(user=new_consultant, record=record).exists():
                new_keys = RecordEncryptionNew(user=new_consultant, record=record, key=record_decryption_key)
                new_keys.encrypt(public_key_user=new_consultant.get_public_key())
                new_keys.save()

            return Response({"action": "matched"})
        else:
            pool_record = PoolRecord(record=record, record_key=record_decryption_key)
            pool_record.save()
            return_val = PoolRecordSerializer(pool_record).data
            return_val.update({"action": "created"})
            return Response(return_val)

    @action(detail=False, methods=['get'])
    def status(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_CAN_CONSULT):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        queryset = PoolRecord.objects.filter(record__template__rlc=user.rlc)
        if queryset.count() > 0:
            data = PoolRecordSerializer(queryset, many=True).data
            return_val = {"type": "records"}
            return_val.update({"entries": data})
            return Response(return_val)

        queryset = PoolConsultant.objects.filter(consultant__rlc=user.rlc)
        if queryset.count() > 0:
            data = PoolConsultantSerializer(queryset, many=True).data
            return_val = {"type": "consultants"}
            return_val.update({"entries": data})
            number_of_own_enlistings = PoolConsultant.objects.filter(
                consultant=user
            ).count()
            return_val.update({"number_of_own_enlistings": number_of_own_enlistings})
            return Response(return_val)

        return Response({"type": "empty"})
