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
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.recordmanagement import models, serializers
from backend.recordmanagement.models.encrypted_record import EncryptedRecord
from backend.recordmanagement.models.encrypted_record_message import EncryptedRecordMessage
from backend.static import error_codes
from backend.static.emails import EmailSender
from backend.static.middleware import get_private_key_from_request


class EncryptedRecordMessageViewSet(viewsets.ModelViewSet):
    queryset = EncryptedRecordMessage.objects.all()
    serializer_class = serializers.EncryptedRecordMessageSerializer


class EncryptedRecordMessageByRecordViewSet(APIView):
    def post(self, request, id):
        if "message" not in request.data or request.data["message"] == "":
            raise CustomError(error_codes.ERROR__RECORD__MESSAGE__NO_MESSAGE_PROVIDED)
        users_private_key = get_private_key_from_request(request)

        try:
            e_record = EncryptedRecord.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        if not e_record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        (
            record_message,
            record_key,
        ) = EncryptedRecordMessage.objects.create_encrypted_record_message(
            sender=request.user,
            message=request.data["message"],
            record=e_record,
            senders_private_key=users_private_key,
        )

        return Response(
            serializers.EncryptedRecordMessageSerializer(
                record_message
            ).get_decrypted_data(record_key)
        )

    def get(self, request, id):
        pass
