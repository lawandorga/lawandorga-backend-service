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
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from backend.recordmanagement.serializers import (
    EncryptedRecordDetailSerializer,
    EncryptedRecordSerializer,
    OldEncryptedClientSerializer,
    OriginCountrySerializer,
    OldEncryptedRecordDocumentSerializer,
    EncryptedRecordMessageDetailSerializer,
    EncryptedRecordListSerializer,
    EncryptedRecordMessageSerializer,
    EncryptedRecordPermissionSerializer, RecordDocumentSerializer,
)
from backend.recordmanagement.models import (
    EncryptedRecordPermission,
    RecordEncryption,
    EncryptedClient,
    EncryptedRecord,
    EncryptedRecordMessage,
)
from backend.static.serializers import map_values
from backend.static.encryption import AESEncryption
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.request import Request
from backend.static.emails import EmailSender
from backend.api.errors import CustomError
from backend.api.models import UserProfile, Notification
from django.db.models import Q, QuerySet, Case, When, Value, IntegerField
from backend.static import error_codes, permissions
from rest_framework import status, viewsets
from django.conf import settings
from typing import Any


class EncryptedRecordViewSet(viewsets.ModelViewSet):
    queryset = EncryptedRecord.objects.none()
    pagination_class = LimitOffsetPagination
    serializer_class = EncryptedRecordSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return EncryptedRecordListSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        return EncryptedRecord.objects.filter(from_rlc=self.request.user.rlc).prefetch_related('working_on_record',
                                                                                               'tagged', 'tags')

    def list(self, request, *args, **kwargs):
        if (
            not request.user.has_permission(permissions.PERMISSION_VIEW_RECORDS_RLC) and
            not request.user.has_permission(permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC)
        ):
            raise PermissionDenied()

        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # permission stuff
        if not request.user.has_permission(
            permissions.PERMISSION_CAN_ADD_RECORD_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # set the client data
        client_data = map_values(
            {
                "birthday": "birthday",
                "name": "name",
                "phone_number": "phone_number",
                "note": "note",
                "origin_country": "origin_country",
            },
            request.data,
        )

        # validate the data
        client_serializer = OldEncryptedClientSerializer(data=client_data)
        client_serializer.is_valid(raise_exception=True)
        data = client_serializer.validated_data

        # create the client
        client = EncryptedClient(**data)
        client.encrypt(request.user.rlc.get_public_key())
        client.save()

        # set the record data
        record_data = map_values(
            {
                "record_token": "record_token",
                "first_contact_date": "first_contact_date",
                "working_on_record": "working_on_record",
                "tags": "tags",
            },
            request.data,
        )
        record_data["state"] = "op"
        record_data["creator"] = request.user.pk
        record_data["from_rlc"] = request.user.rlc.pk
        record_data["client"] = client.pk

        # validate the record data
        record_serializer = EncryptedRecordSerializer(data=record_data)
        record_serializer.is_valid(raise_exception=True)

        # remove many to many because record needs a pk first
        working_on_record = record_serializer.validated_data.pop("working_on_record")
        tags = record_serializer.validated_data.pop("tags")
        data = record_serializer.validated_data

        # create the record
        aes_key = AESEncryption.generate_secure_key()
        record = EncryptedRecord(**data)
        record.encrypt(aes_key=aes_key)
        record.save()

        # add many to many
        for item in working_on_record:
            record.working_on_record.add(item)
        for item in tags:
            record.tags.add(item)

        # create encryption keys
        for user in record.get_users_who_should_be_allowed_to_decrypt().order_by():
            encryption = RecordEncryption(
                user=user, record=record, encrypted_key=aes_key
            )
            encryption.encrypt(user.get_public_key())
            encryption.save()

        # solve a bug when the user who creates the record is not allowed to see his own record
        if not RecordEncryption.objects.filter(user=request.user, record=record).exists():
            encryption = RecordEncryption(
                user=request.user, record=record, encrypted_key=aes_key
            )
            encryption.encrypt(request.user.get_public_key())
            encryption.save()

        # notify about the new record
        Notification.objects.notify_record_created(request.user, record)
        url = settings.FRONTEND_URL + "records/" + str(record.id)
        for user in working_on_record:
            if user != request.user:
                EmailSender.send_new_record(user.email, url)

        # return response
        record.decrypt(
            user=request.user,
            private_key_user=request.user.get_private_key(request=request),
        )
        serializer = self.get_serializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        self.instance: EncryptedRecord = super().get_object()
        self.private_key_user = self.request.user.get_private_key(request=self.request)
        self.instance.decrypt(user=self.request.user, private_key_user=self.private_key_user)
        return self.instance

    def perform_update(self, serializer):
        for attr, value in serializer.validated_data.items():
            if attr == 'working_on_record':
                for consultant in value:
                    if not RecordEncryption.objects.filter(user=consultant, record=self.instance).exists():
                        key = self.instance.get_decryption_key(self.request.user, self.private_key_user)
                        encryption = RecordEncryption(user=consultant, record=self.instance, encrypted_key=key)
                        encryption.encrypt(consultant.get_public_key())
                        encryption.save()
                self.instance.working_on_record.set(value)
            elif attr == 'tagged':
                self.instance.tagged.set(value)
            elif attr == 'tags':
                self.instance.tags.set(value)
            else:
                setattr(self.instance, attr, value)
        self.instance.encrypt(user=self.request.user, private_key_user=self.private_key_user)
        self.instance.save()
        self.instance.decrypt(user=self.request.user, private_key_user=self.private_key_user)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        record = self.get_object()
        if request.user.has_permission(
            permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
            for_rlc=request.user.rlc,
        ):
            record.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def request_permission(self, request, *args, **kwargs):
        record = super().get_object()

        record_permission = EncryptedRecordPermission.objects.create(
            request_from=request.user, record=record
        )

        Notification.objects.notify_record_permission_requested(
            request.user, record_permission
        )

        return Response(EncryptedRecordPermissionSerializer(record_permission).data)

    @action(detail=True, methods=['get'])
    def messages(self, request, *args, **kwargs):
        record = self.get_object()
        messages = record.messages.all()
        messages_data = []
        for message in list(messages):
            message.decrypt(user=request.user, private_key_user=self.private_key_user)
            messages_data.append(EncryptedRecordMessageDetailSerializer(message).data)
        return Response(messages_data)

    @action(detail=True, methods=['get'])
    def documents(self, request, *args, **kwargs):
        record = self.get_object()
        documents = record.e_record_documents.all()
        return Response(RecordDocumentSerializer(documents, many=True).data)

    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None):
        # get the record
        record = self.get_object()

        # permission stuff
        if not record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # get the private key of the user for later
        private_key_user = request.user.get_private_key(request=request)

        # set the data
        request.data["record"] = record.pk
        request.data["sender"] = request.user.pk

        # validate the data
        message_serializer = EncryptedRecordMessageSerializer(data=request.data)
        message_serializer.is_valid(raise_exception=True)
        data = message_serializer.validated_data

        # create the message
        message = EncryptedRecordMessage(**data)
        message.encrypt(user=request.user, private_key_user=private_key_user)
        message.save()

        # notify about the new message
        Notification.objects.notify_record_message_added(request.user, message)

        # return response
        message.decrypt(user=request.user, private_key_user=private_key_user)
        return Response(
            EncryptedRecordMessageDetailSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )
