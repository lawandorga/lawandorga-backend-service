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

from typing import Any
import logging
from django.conf import settings
from django.db.models import Q, QuerySet, Case, When, Value, IntegerField
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination

from backend.api.errors import CustomError
from backend.api.models import UserProfile
from backend.api.models.notification import Notification
from backend.recordmanagement import models, serializers
from backend.recordmanagement.models.encrypted_client import EncryptedClient
from backend.recordmanagement.models.encrypted_record import EncryptedRecord
from backend.recordmanagement.models.encrypted_record_permission import EncryptedRecordPermission
from backend.recordmanagement.models.origin_country import OriginCountry
from backend.recordmanagement.models.record_encryption import RecordEncryption
from backend.recordmanagement.models.record_tag import RecordTag
from backend.static import error_codes, permissions
from backend.static.emails import EmailSender
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.frontend_links import FrontendLinks
from backend.static.middleware import get_private_key_from_request
from backend.api.permissions import OnlyGet


class EncryptedRecordsListViewSet(viewsets.ModelViewSet):
    queryset = EncryptedRecord.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = serializers.EncryptedRecordNoDetailSerializer
    permission_classes = (OnlyGet,)

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_superuser:
            queryset = EncryptedRecord.objects.all()
        else:
            queryset = EncryptedRecord.objects.filter_by_rlc(
                self.request.user.rlc
            )

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
            from_record_permissions = [
                record_permission.record.id
                for record_permission in list(
                    EncryptedRecordPermission.objects.filter(
                        request_from=user, state="gr", record__id__in=record_ids
                    )
                )
            ]
            from_working_on = [
                record.id
                for record in list(user.working_on_e_record.filter(id__in=record_ids))
            ]
            queryset = queryset.annotate(
                access=Case(
                    When(
                        id__in=from_record_permissions + from_working_on, then=Value(1)
                    ),
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
        """

        :param **kwargs:
        :param request:
        :return:
        """
        user = request.user

        if (
            not user.has_permission(
                permissions.PERMISSION_VIEW_RECORDS_RLC, for_rlc=user.rlc
            )
            and not user.has_permission(
                permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc
            )
            and not user.is_superuser
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        entries = self.get_queryset()
        paginated = self.paginate_queryset(entries)
        data = serializers.EncryptedRecordNoDetailListSerializer(
            paginated, many=True
        ).data
        return self.get_paginated_response(data)


class EncryptedRecordViewSet(APIView):
    def post(self, request):
        data = request.data
        rlc = request.user.rlc
        if not request.user.has_permission(
            permissions.PERMISSION_CAN_ADD_RECORD_RLC, for_rlc=rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        creators_private_key = get_private_key_from_request(request)

        consultants: [UserProfile] = []
        for user_id in data["consultants"]:
            try:
                user: UserProfile = UserProfile.objects.get(pk=user_id)
            except Exception:
                raise CustomError(error_codes.ERROR__RECORD__CONSULTANT__NOT_EXISTING)
            if not user.has_permission(permissions.PERMISSION_CAN_CONSULT, for_rlc=rlc):
                raise CustomError(error_codes.ERROR__RECORD__CONSULTANT__NO_PERMISSION)
            consultants.append(user)

        if "client_id" in data:
            rlcs_private_key = request.user.get_rlcs_private_key(creators_private_key)
            try:
                e_client = EncryptedClient.objects.get(pk=data["client_id"])
            except:
                raise CustomError(error_codes.ERROR__RECORD__CLIENT__NOT_EXISTING)

            client_password = e_client.get_password(rlcs_private_key)

            e_client.note = AESEncryption.encrypt(data["client_note"], client_password)
            e_client.phone_number = AESEncryption.encrypt(
                data["client_phone_number"], client_password
            )
            e_client.save()
        else:
            client_key = AESEncryption.generate_secure_key()
            e_client = EncryptedClient(
                birthday=data["client_birthday"], from_rlc=rlc
            )
            e_client.name = AESEncryption.encrypt(data["client_name"], client_key)
            e_client.phone_number = AESEncryption.encrypt(
                data["client_phone_number"], client_key
            )
            e_client.note = AESEncryption.encrypt(data["client_note"], client_key)
            e_client.save()

            rlcs_public_key = request.user.get_rlcs_public_key()
            e_client.encrypted_client_key = RSAEncryption.encrypt(
                client_key, rlcs_public_key
            )
            e_client.save()

        try:
            origin = OriginCountry.objects.get(pk=data["origin_country"])
        except:
            raise CustomError(error_codes.ERROR__RECORD__ORIGIN_COUNTRY__NOT_FOUND)
        e_client.origin_country = origin
        e_client.save()

        e_record = EncryptedRecord(
            client_id=e_client.id,
            first_contact_date=data["first_contact_date"],
            last_contact_date=data["first_contact_date"],
            record_token=data["record_token"],
            creator_id=request.user.id,
            from_rlc_id=rlc.id,
            state="op",
        )
        record_key = AESEncryption.generate_secure_key()
        e_record.note = AESEncryption.encrypt(data["record_note"], record_key)
        e_record.save()

        for tag_id in data["tags"]:
            e_record.tagged.add(RecordTag.objects.get(pk=tag_id))
        for consultant in consultants:
            e_record.working_on_record.add(consultant)

        e_record.save()

        users_with_keys = e_record.get_users_with_decryption_keys()
        for user in users_with_keys:
            users_public_key = user.get_public_key()

            encrypted_record_key = RSAEncryption.encrypt(record_key, users_public_key)
            record_encryption = RecordEncryption(
                user=user, record=e_record, encrypted_key=encrypted_record_key
            )
            record_encryption.save()
        e_record.save()  # TODO: why?

        Notification.objects.notify_record_created(request.user, e_record)

        if not settings.DEBUG:
            url = FrontendLinks.get_record_link(e_record)
            for user in consultants:
                if user != request.user:
                    EmailSender.send_new_record(user.email, url)

        return Response(
            serializers.EncryptedRecordFullDetailSerializer(
                e_record
            ).get_decrypted_data(record_key),
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, id) -> Response:
        try:
            e_record: EncryptedRecord = EncryptedRecord.objects.get(pk=id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)

        user = request.user
        if user.rlc != e_record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if e_record.user_has_permission(user):
            users_private_key = get_private_key_from_request(request)
            record_key = e_record.get_decryption_key(user, users_private_key)
            record_data = serializers.EncryptedRecordFullDetailSerializer(
                e_record
            ).get_decrypted_data(record_key)
            rlcs_private_key = user.get_rlcs_private_key(users_private_key)
            client_password = e_record.client.get_password(rlcs_private_key)
            client_serializer = serializers.EncryptedClientSerializer(
                e_record.client
            ).get_decrypted_data(client_password)
            origin_country = serializers.OriginCountrySerializer(
                e_record.client.origin_country
            )
            documents = serializers.EncryptedRecordDocumentSerializer(
                e_record.e_record_documents, many=True
            )
            messages = serializers.EncryptedRecordMessageSerializer(
                e_record.e_record_messages, many=True
            ).get_decrypted_data(record_key)
            return Response(
                {
                    "record": record_data,
                    "client": client_serializer,
                    "origin_country": origin_country.data,
                    "record_documents": documents.data,
                    "record_messages": messages,
                }
            )
        else:
            serializer = serializers.EncryptedRecordNoDetailSerializer(e_record)
            permission_request = EncryptedRecordPermission.objects.filter(
                record=e_record, request_from=user, state="re"
            ).first()

            if not permission_request:
                state = "nr"
            else:
                state = permission_request.state
            return Response({"record": serializer.data, "request_state": state})

    def patch(self, request, id):
        try:
            e_record = EncryptedRecord.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)
        user = request.user
        if user.rlc != e_record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if not e_record.user_has_permission(user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        users_private_key = get_private_key_from_request(request)
        record_key = e_record.get_decryption_key(user, users_private_key)
        rlcs_private_key = user.get_rlcs_private_key(users_private_key)
        client = e_record.client
        client_key = client.get_password(rlcs_private_key)

        record_patched = []
        if "record" in request.data:
            record_data: dict = request.data["record"]
            record_patched = e_record.patch(
                record_data=record_data, record_key=record_key
            )
        client_patched = []
        if "client" in request.data:
            client_data = request.data["client"]
            client_patched = client.patch(
                client_data=client_data, clients_aes_key=client_key
            )

        notification_text = ",".join(record_patched + client_patched)
        Notification.objects.notify_record_patched(user, e_record, notification_text)

        record_from_db = EncryptedRecord.objects.get(pk=e_record.id)
        client_from_db = EncryptedClient.objects.get(pk=client.id)
        decrypted_record_data = serializers.EncryptedRecordFullDetailSerializer(
            record_from_db
        ).get_decrypted_data(record_key)
        decrypted_client_data = serializers.EncryptedClientSerializer(
            client_from_db
        ).get_decrypted_data(client_key)

        return Response(
            {"record": decrypted_record_data, "client": decrypted_client_data}
        )

    def delete(self, request, id):
        try:
            record = Record.objects.get(pk=id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        user = request.user
        if user.rlc != record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if (
            user.has_permission(
                permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
                for_rlc=user.rlc,
            )
            or user.is_superuser
        ):
            record.delete()
        return Response()
