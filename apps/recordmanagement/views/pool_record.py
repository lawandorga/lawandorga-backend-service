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
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.api.errors import CustomError
from apps.recordmanagement.models.encrypted_record import EncryptedRecord
from apps.recordmanagement.models.pool_consultant import PoolConsultant
from apps.recordmanagement.models.pool_record import PoolRecord
from apps.recordmanagement.models.record_encryption import RecordEncryption
from apps.recordmanagement.serializers import PoolRecordSerializer
from apps.static import error_codes
from apps.static.middleware import get_private_key_from_request
from apps.static.permissions import PERMISSION_CAN_CONSULT


class PoolRecordViewSet(viewsets.ModelViewSet):
    queryset = PoolRecord.objects.all()
    serializer_class = PoolRecordSerializer

    def create(self, request, *args, **kwargs):
        record = get_object_or_404(EncryptedRecord, pk=request.data['record'])

        if PoolRecord.objects.filter(record=record, yielder=request.user).exists():
            data = {'detail': 'This record is already in the record pool.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not record.working_on_record.filter(pk=request.user.pk).exists():
            data = {'detail': 'You need to be a consultant of this record in order to be able to yield it.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        private_key = request.user.get_private_key(request=request)
        record_decryption_key = record.get_decryption_key(request.user, private_key)

        if PoolConsultant.objects.filter(consultant__rlc=request.user.rlc).count() >= 1:
            entry = PoolConsultant.objects.filter(consultant__rlc=request.user.rlc).order_by(
                "enlisted"
            )[0]
            new_consultant = entry.consultant
            entry.delete()

            RecordEncryption.objects.filter(record=record, user=request.user).delete()
            new_keys = RecordEncryption(
                user=new_consultant,
                record=record,
                encrypted_key=new_consultant.rsa_encrypt(record_decryption_key),
            )
            new_keys.save()

            record.working_on_record.remove(request.user)
            record.working_on_record.add(new_consultant)
            record.save()

            return Response({"action": "matched"})
        else:
            pool_record = PoolRecord(
                record=record, yielder=request.user, record_key=record_decryption_key
            )
            pool_record.save()
            return_val = PoolRecordSerializer(pool_record).data
            return_val.update({"action": "created"})
            return Response(return_val)

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_CAN_CONSULT, for_rlc=request.user.rlc):
            raise PermissionDenied()
        queryset = PoolRecord.objects.filter(record__from_rlc=request.user.rlc)
        data = PoolRecordSerializer(queryset, many=True).data
        return Response(data)
