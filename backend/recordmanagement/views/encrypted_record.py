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
from django.core import paginator
from rest_framework.decorators import action

from backend.recordmanagement.serializers import (
    EncryptedRecordDetailSerializer,
    EncryptedRecordSerializer,
    OldEncryptedClientSerializer,
    OriginCountrySerializer,
    EncryptedRecordDocumentSerializer,
    EncryptedRecordMessageDetailSerializer,
    EncryptedRecordListSerializer,
    EncryptedRecordMessageSerializer,
    EncryptedRecordPermissionSerializer,
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

    def get_queryset(self) -> QuerySet:
        return EncryptedRecord.objects.filter(from_rlc=self.request.user.rlc)

    def get_queryset_2(self) -> QuerySet:
        queryset = EncryptedRecord.objects.filter(from_rlc=self.request.user.rlc)

        request: Request = self.request
        user: UserProfile = request.user
        query_params = request.query_params

        if "filter" in query_params and query_params["filter"] != "":
            parts = query_params["filter"].split(" ")

            for part in parts:
                consultants = UserProfile.objects.filter(name__icontains=part)
                queryset = queryset.filter(
                    Q(tagged__name__icontains=part)
                    | Q(note__icontains=part)
                    | Q(working_on_record__in=consultants)
                    | Q(record_token__icontains=part)
                ).distinct()

        if user.is_superuser or user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc
        ):
            queryset = queryset.annotate(access=Value(1, output_field=IntegerField()))
        else:
            record_ids = [single_record.id for single_record in list(queryset)]

            record_ids_from_keys = [
                key.record.id
                for key in list(
                    RecordEncryption.objects.filter(user=user, record__in=record_ids)
                )
            ]

            queryset = queryset.annotate(
                access=Case(
                    When(id__in=record_ids_from_keys, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )

        if "sort" in request.query_params:
            if (
                "sortdirection" in request.query_params
                and request.query_params["sortdirection"] == "desc"
            ):
                to_sort = "-" + request.query_params["sort"]
            else:
                to_sort = request.query_params["sort"]
        else:
            to_sort = "-access"

        queryset = queryset.order_by(to_sort)

        return queryset

    def list(self, request: Request, **kwargs: Any):
        user = request.user

        if not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_RLC, for_rlc=user.rlc
        ) and not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        entries = self.get_queryset_2()
        paginated = self.paginate_queryset(entries)
        data = EncryptedRecordListSerializer(paginated, many=True).data
        return self.get_paginated_response(data)

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
                "tagged": "tagged",
            },
            request.data,
        )
        record_data["state"] = "op"
        record_data["creator"] = request.user.pk
        record_data["from_rlc"] = request.user.rlc.pk
        record_data["client"] = client.pk

        # validate the record data
        record_serializer = self.get_serializer(data=record_data)
        record_serializer.is_valid(raise_exception=True)

        # remove many to many because record needs a pk first
        working_on_record = record_serializer.validated_data.pop("working_on_record")
        tagged = record_serializer.validated_data.pop("tagged")
        data = record_serializer.validated_data

        # create the record
        aes_key = AESEncryption.generate_secure_key()
        record = EncryptedRecord(**data)
        record.encrypt(aes_key=aes_key)
        record.save()

        # add many to many
        for item in working_on_record:
            record.working_on_record.add(item)
        for item in tagged:
            record.tagged.add(item)

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

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        record = self.get_object()

        if request.user.record_encryptions.filter(record=record).exists():
            private_key_user = request.user.get_private_key(request=request)
            private_key_rlc = request.user.rlc.get_private_key(
                request.user, private_key_user
            )

            # decrypt record
            record.decrypt(request.user, private_key_user)

            # add client data
            client = record.client
            client.decrypt(private_key_rlc)

            # add origin country
            origin_country = client.origin_country

            # add documents
            documents = record.e_record_documents

            # add messages
            messages = record.messages.all()
            messages_data = []
            for message in list(messages):
                message.decrypt(user=request.user, private_key_user=private_key_user)
                messages_data.append(
                    EncryptedRecordMessageDetailSerializer(message).data
                )

            return Response(
                {
                    "record": EncryptedRecordDetailSerializer(record).data,
                    "client": OldEncryptedClientSerializer(client).data,
                    "origin_country": OriginCountrySerializer(origin_country).data,
                    "record_documents": EncryptedRecordDocumentSerializer(
                        documents, many=True
                    ).data,
                    "record_messages": messages_data,
                }
            )
        else:
            record.reset_encrypted_fields()
            serializer = self.get_serializer(record)
            permission_request = EncryptedRecordPermission.objects.filter(
                record=record, request_from=request.user, state="re"
            ).first()
            if not permission_request:
                state = "nr"
            else:
                state = permission_request.state
            return Response({"record": serializer.data, "request_state": state})

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # get the record to be updated
        record = self.get_object()

        # permission stuff
        if not record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # get the private keys
        private_key_user = request.user.get_private_key(request=request)
        private_key_rlc = request.user.rlc.get_private_key(
            request.user, private_key_user
        )
        public_key_rlc = request.user.rlc.get_public_key()

        # decrypt the record
        record.decrypt(user=request.user, private_key_user=private_key_user)

        # get the client of the record
        client = record.client
        client.decrypt(private_key_rlc)

        # check that the data is valid
        partial = kwargs.pop("partial", False)
        if "record" not in request.data:
            request.data["record"] = {}
        record_serializer = self.get_serializer(
            record, data=request.data["record"], partial=partial
        )
        record_serializer.is_valid(raise_exception=True)
        if "client" not in request.data:
            request.data["client"] = {}
        client_serializer = OldEncryptedClientSerializer(
            client, data=request.data["client"], partial=partial
        )
        client_serializer.is_valid(raise_exception=True)

        # update the client
        for attr, value in client_serializer.validated_data.items():
            setattr(client, attr, value)
        client.encrypt(public_key_rlc)
        client.save()

        # update the record
        for attr, value in record_serializer.validated_data.items():
            setattr(record, attr, value)
        record.encrypt(request.user, private_key_user)
        record.save()

        # create a notification about this change
        notification_text = "{}, {}".format(record, client)
        Notification.objects.notify_record_patched(
            request.user, record, notification_text
        )

        # return valid data
        record.decrypt(user=request.user, private_key_user=private_key_user)
        client.decrypt(private_key_rlc=private_key_rlc)
        return Response(
            {
                "record": self.get_serializer(record).data,
                "client": OldEncryptedClientSerializer(client).data,
            }
        )

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
        record = self.get_object()

        record_permission = EncryptedRecordPermission.objects.create(
            request_from=request.user, record=record
        )

        Notification.objects.notify_record_permission_requested(
            request.user, record_permission
        )

        return Response(EncryptedRecordPermissionSerializer(record_permission).data)

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
