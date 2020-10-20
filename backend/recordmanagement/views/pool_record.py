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

from rest_framework import viewsets
from rest_framework.response import Response

from backend.api.errors import CustomError
from backend.recordmanagement.models import (
    EncryptedRecord,
    PoolConsultant,
    PoolRecord,
    RecordEncryption,
)
from backend.recordmanagement.serializers import PoolRecordSerializer
from backend.static import error_codes
from backend.static.middleware import get_private_key_from_request
from backend.static.permissions import PERMISSION_CAN_CONSULT


class PoolRecordViewSet(viewsets.ModelViewSet):
    queryset = PoolRecord.objects.all()
    serializer_class = PoolRecordSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        private_key = get_private_key_from_request(request)
        if "record" not in request.data:
            raise CustomError(error_codes.ERROR__API__ID_NOT_PROVIDED)
        try:
            record = EncryptedRecord.objects.get(pk=request.data["record"])
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)

        if PoolRecord.objects.filter(record=record, yielder=user).count() > 0:
            raise CustomError(error_codes.ERROR__API__ALREADY_REQUESTED)

        try:
            record.working_on_record.get(pk=user.id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__NOT_WORKING_ON)
        record_decryption_key = record.get_decryption_key(user, private_key)

        if PoolConsultant.objects.filter(consultant__rlc=user.rlc).count() >= 1:
            entry = PoolConsultant.objects.filter(consultant__rlc=user.rlc).order_by(
                "enlisted"
            )[0]
            new_consultant = entry.consultant
            entry.delete()

            new_keys = RecordEncryption(
                user=new_consultant,
                record=record,
                encrypted_key=new_consultant.rsa_encrypt(record_decryption_key),
            )
            new_keys.save()
            RecordEncryption.objects.filter(record=record, user=user).delete()

            record.working_on_record.remove(user)
            record.working_on_record.add(new_consultant)
            record.save()

            return Response({"action": "matched"})
        else:
            pool_record = PoolRecord(
                record=record, yielder=user, record_key=record_decryption_key
            )
            pool_record.save()
            return_val = PoolRecordSerializer(pool_record).data
            return_val.update({"action": "created"})
            return Response(return_val)

    def list(self, request, *args, **kwargs):
        user = request.user
        if not user.has_permission(PERMISSION_CAN_CONSULT, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        queryset = PoolRecord.objects.filter(record__from_rlc=user.rlc)
        data = PoolRecordSerializer(queryset, many=True).data
        return Response(data)
