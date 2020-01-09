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
from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.api.models import UserProfile, UserEncryptionKeys
from backend.recordmanagement import models, serializers
from backend.static import error_codes, permissions
from backend.static.date_utils import parse_date
from backend.static.emails import EmailSender
from backend.static.frontend_links import FrontendLinks
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.middleware import get_private_key_from_request


class EncryptedRecordsListViewSet(viewsets.ViewSet):
    def list(self, request):
        """

        :param request:
        :return:
        """
        parts = request.query_params.get('search', '').split(' ')
        user = request.user

        if user.is_superuser:
            entries = models.EncryptedRecord.objects.all()
            for part in parts:
                consultants = UserProfile.objects.filter(name__icontains=part)
                entries = entries.filter(
                    Q(tagged__name__icontains=part) | Q(note__icontains=part) | Q(
                        working_on_e_record__in=consultants) | Q(record_token__icontains=part)).distinct()
            serializer = serializers.EncryptedRecordFullDetailSerializer(entries, many=True)
            return Response(serializer.data)

        if not user.has_permission(permissions.PERMISSION_VIEW_RECORDS_RLC,
                                   for_rlc=user.rlc) and not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        entries = models.EncryptedRecord.objects.filter_by_rlc(user.rlc)
        for part in parts:
            consultants = UserProfile.objects.filter(name__icontains=part)
            entries = entries.filter(
                Q(tagged__name__icontains=part) | Q(note__icontains=part) | Q(
                    working_on_e_record__in=consultants) | Q(record_token__icontains=part)).distinct()

        records = []
        if user.has_permission(permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc):
            queryset = entries
            serializer = serializers.EncryptedRecordFullDetailSerializer(queryset, many=True)
            records += serializer.data
        else:
            queryset = entries.get_full_access_e_records(user).distinct()
            serializer = serializers.EncryptedRecordFullDetailSerializer(queryset, many=True)
            records += serializer.data

            queryset = entries.get_no_access_e_records(user)
            serializer = serializers.EncryptedRecordNoDetailSerializer(queryset, many=True)
            records += serializer.data
        return Response(records)

    def create(self, request):
        """outdated"""
        pass
        rlc = request.user.rlc
        e_record = models.EncryptedRecord(client_id=request.data['client'], first_contact_date=request.data['first_contact_date'],
                               last_contact_date=request.data['last_contact_date'],
                               record_token=request.data['record_token'],
                               creator_id=request.user.id,
                               from_rlc_id=rlc.id)
        # e_record.save()
        # TODO: remove?
        record_key = AESEncryption.generate_secure_key()
        e_record.note = AESEncryption.encrypt(request.data['note'], record_key)
        e_record.save()

        for tag_id in request.data['tagged']:
            e_record.tagged.add(models.RecordTag.objects.get(pk=tag_id))
        for user_id in request.data['working_on_record']:
            try:
                user = UserProfile.objects.get(pk=user_id)
            except Exception:
                raise CustomError(error_codes.ERROR__RECORD__CONSULTANT__NOT_EXISTING)
            e_record.working_on_record.add(user)

            encryption_keys = models.RecordEncryption
        e_record.save()

        return Response(serializers.RecordFullDetailSerializer(e_record).data)


class RecordViewSet(APIView):
    def post(self, request):
        if not request.user.has_permission(permissions.PERMISSION_CAN_ADD_RECORD_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        data = request.data
        rlc = request.user.rlc
        creators_private_key = get_private_key_from_request(request)

        if 'client_id' in data:
            # TODO: ! encryption, how to access already existing client?
            rlcs_private_key = request.user.get_rlcs_private_key(creators_private_key)
            try:
                e_client = models.EncryptedClient.objects.get(pk=data['client_id'])
            except:
                raise CustomError(error_codes.ERROR__RECORD__CLIENT__NOT_EXISTING)

            client_password = e_client.get_password(rlcs_private_key)

            e_client.note = AESEncryption.encrypt(data['client_note'], client_password)
            e_client.phone_number = AESEncryption.encrypt(data['client_phone_number'], client_password)
            e_client.save()
        else:
            client_key = AESEncryption.generate_secure_key()
            e_client = models.EncryptedClient(birthday=data['client_birthday'], from_rlc=rlc)
            e_client.name = AESEncryption.encrypt(data['client_name'], client_key)
            e_client.phone_number = AESEncryption.encrypt(data['client_phone_number'], client_key)
            e_client.note = AESEncryption.encrypt(data['client_note'], client_key)
            e_client.save()

            rlcs_public_key = request.user.get_rlcs_public_key()
            e_client.encrypted_client_key = RSAEncryption.encrypt(client_key, rlcs_public_key)
            e_client.save()

        try:
            origin = models.OriginCountry.objects.get(pk=data['origin_country'])
        except:
            raise CustomError(error_codes.ERROR__RECORD__ORIGIN_COUNTRY__NOT_FOUND)
        e_client.origin_country = origin
        e_client.save()

        e_record = models.EncryptedRecord(client_id=e_client.id, first_contact_date=data['first_contact_date'],
                               last_contact_date=data['first_contact_date'], record_token=data['record_token'],
                               creator_id=request.user.id, from_rlc_id=rlc.id, state="op")
        record_key = AESEncryption.generate_secure_key()
        e_record.note = AESEncryption.encrypt(data['note'], record_key)
        e_record.save()

        for tag_id in data['tags']:
            e_record.tagged.add(models.RecordTag.objects.get(pk=tag_id))
        for user_id in data['consultants']:
            try:
                user = UserProfile.objects.get(pk=user_id)
            except Exception:
                raise CustomError(error_codes.ERROR__RECORD__CONSULTANT__NOT_EXISTING)
            e_record.working_on_record.add(user)
        e_record.save()

        users_with_keys = e_record.get_users_with_decryption_keys()
        for user in users_with_keys:
            users_public_key = UserEncryptionKeys.objects.get_users_public_key(user)

            encrypted_record_key = RSAEncryption.encrypt(record_key, users_public_key)
            record_encryption = models.RecordEncryption(user=user, record=e_record, encrypted_key=encrypted_record_key)
            record_encryption.save()

            encrypted_client_key = RSAEncryption.encrypt(client_key, users_public_key)
            client_encryption = models.ClientEncryption(user=user, client=e_client, encrypted_key=encrypted_client_key)
            client_encryption.save()
        e_record.save()

        if not settings.DEBUG:
            for user_id in data['consultants']:
                actual_consultant = UserProfile.objects.get(pk=user_id)
                url = FrontendLinks.get_record_link(e_record)
                EmailSender.send_email_notification([actual_consultant.email], "New Record",
                                                    "RLC Intranet Notification - Your were assigned as a consultant for a new record. Look here:" +
                                                    url)

        return Response(serializers.EncryptedRecordFullDetailSerializer(e_record).data)

    def get(self, request, id):
        users_private_key = get_private_key_from_request(request)

        try:
            e_record = models.EncryptedRecord.objects.get(pk=id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        if 'private_key' not in request.data:
            raise CustomError(error_codes.ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED)
        users_private_key = request.data['private_key']

        user = request.user
        if user.rlc != e_record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if e_record.user_has_permission(user):
            record_serializer = serializers.EncryptedRecordFullDetailSerializer(e_record).get_decrypted_data(users_private_key)
            client_serializer = serializers.EncryptedClientSerializer(e_record.client)
            origin_country = serializers.OriginCountrySerializer(e_record.client.origin_country)
            documents = serializers.EncryptedRecordDocumentSerializer(e_record.record_documents, many=True)
            messages = serializers.EncryptedRecordMessage(e_record.record_messages, many=True)

            return Response({
                'record': record_serializer.data,
                'client': client_serializer.data,
                'origin_country': origin_country.data,
                'record_documents': documents.data,
                'record_messages': messages.data
            })
        else:
            serializer = serializers.RecordNoDetailSerializer(e_record)
            permission_request = models.RecordPermission.objects.filter(record=e_record, request_from=user,
                                                                        state='re').first()

            if not permission_request:
                state = 'nr'
            else:
                state = permission_request.state
            return Response({
                'record': serializer.data,
                'request_state': state
            })

    def patch(self, request, id):
        record = models.Record.objects.get(pk=id)
        user = request.user
        if user.rlc != record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if not record.user_has_permission(user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        record_data = request.data['record']
        client_data = request.data['client']
        client = record.client

        try:
            record.record_token = record_data['token']
            record.note = record_data['note']
            record.contact = record_data['contact']
            record.last_contact_date = parse_date(record_data['last_contact_date'])
            record.state = record_data['state']
            record.official_note = record_data['official_note']
            record.additional_facts = record_data['additional_facts']
            record.bamf_token = record_data['bamf_token']
            record.foreign_token = record_data['foreign_token']
            record.first_correspondence = record_data['first_correspondence']
            record.circumstances = record_data['circumstances']
            record.lawyer = record_data['lawyer']
            record.related_persons = record_data['related_persons']
            record.consultant_team = record_data['consultant_team']
            record.next_steps = record_data['next_steps']
            record.status_described = record_data['status_described']

            record.tagged.clear()
            for tag in record_data['tags']:
                record.tagged.add(models.RecordTag.objects.get(pk=tag['id']))

            client.note = client_data['note']
            client.name = client_data['name']
            client.birthday = parse_date(client_data['birthday'])
            client.origin_country = models.OriginCountry.objects.get(pk=client_data['origin_country'])
            client.phone_number = client_data['phone_number']
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__COULD_NOT_SAVE)

        record.last_edited = datetime.utcnow().replace(tzinfo=pytz.utc)
        record.save()
        client.last_edited = datetime.utcnow().replace(tzinfo=pytz.utc)
        client.save()

        record_url = FrontendLinks.get_record_link(record)
        for user in record.working_on_record.all():
            EmailSender.send_email_notification([user.email], "Patched Record",
                                                "RLC Intranet Notification - A record of yours was changed. Look here:" +
                                                record_url)

        return Response(
            {
                'record': serializers.RecordFullDetailSerializer(models.Record.objects.get(pk=record.pk)).data,
                'client': serializers.ClientSerializer(models.Client.objects.get(pk=client.pk)).data
            }
        )

    def delete(self, request, id):
        try:
            record = models.Record.objects.get(pk=id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        user = request.user
        if user.rlc != record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if user.has_permission(permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
                               for_rlc=user.rlc) or user.is_superuser:
            record.delete()
        return Response()
