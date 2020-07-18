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
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.api.models import Notification, UserEncryptionKeys, UserProfile
from backend.recordmanagement import models, serializers
from backend.static import error_codes, permissions
from backend.static.date_utils import parse_date
from backend.static.emails import EmailSender
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.frontend_links import FrontendLinks
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
                        working_on_record__in=consultants) | Q(record_token__icontains=part)).distinct()
            serializer = serializers.EncryptedRecordNoDetailSerializer(entries, many=True)
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
                    working_on_record__in=consultants) | Q(record_token__icontains=part)).distinct()
        data = serializers.EncryptedRecordNoDetailSerializer(entries, many=True).add_has_permission(user)
        return Response(data)


class EncryptedRecordViewSet(APIView):
    def post(self, request):
        data = request.data
        rlc = request.user.rlc
        if not request.user.has_permission(permissions.PERMISSION_CAN_ADD_RECORD_RLC, for_rlc=rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        creators_private_key = get_private_key_from_request(request)

        consultants: [UserProfile] = []
        for user_id in data['consultants']:
            try:
                user: UserProfile = UserProfile.objects.get(pk=user_id)
            except Exception:
                raise CustomError(error_codes.ERROR__RECORD__CONSULTANT__NOT_EXISTING)
            if not user.has_permission(permissions.PERMISSION_CAN_CONSULT, for_rlc=rlc):
                raise CustomError(error_codes.ERROR__RECORD__CONSULTANT__NO_PERMISSION)
            consultants.append(user)

        if 'client_id' in data:
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
                                          last_contact_date=data['first_contact_date'],
                                          record_token=data['record_token'],
                                          creator_id=request.user.id, from_rlc_id=rlc.id, state="op")
        record_key = AESEncryption.generate_secure_key()
        e_record.note = AESEncryption.encrypt(data['record_note'], record_key)
        e_record.save()

        for tag_id in data['tags']:
            e_record.tagged.add(models.RecordTag.objects.get(pk=tag_id))
        for consultant in consultants:
            e_record.working_on_record.add(consultant)

        e_record.save()

        users_with_keys = e_record.get_users_with_decryption_keys()
        for user in users_with_keys:
            users_public_key = UserEncryptionKeys.objects.get_users_public_key(user)

            encrypted_record_key = RSAEncryption.encrypt(record_key, users_public_key)
            record_encryption = models.RecordEncryption(user=user, record=e_record, encrypted_key=encrypted_record_key)
            record_encryption.save()
        e_record.save()  # TODO: why?

        for user in consultants:
            if user != request.user:
                Notification.objects.create_notification_new_record(str(e_record.id), user, request.user,
                                                                    e_record.record_token)

        if not settings.DEBUG:
            url = FrontendLinks.get_record_link(e_record)
            for user in consultants:
                EmailSender.send_new_record(user.email, url)

        return Response(serializers.EncryptedRecordFullDetailSerializer(e_record).get_decrypted_data(record_key),
                        status=status.HTTP_201_CREATED)

    def get(self, request, id):
        try:
            e_record: models.EncryptedRecord = models.EncryptedRecord.objects.get(pk=id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)

        user = request.user
        if user.rlc != e_record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if e_record.user_has_permission(user):
            users_private_key = get_private_key_from_request(request)
            record_key = e_record.get_decryption_key(user, users_private_key)
            record_data = serializers.EncryptedRecordFullDetailSerializer(e_record).get_decrypted_data(record_key)
            rlcs_private_key = user.get_rlcs_private_key(users_private_key)
            client_password = e_record.client.get_password(rlcs_private_key)
            client_serializer = serializers.EncryptedClientSerializer(e_record.client).get_decrypted_data(
                client_password)
            origin_country = serializers.OriginCountrySerializer(e_record.client.origin_country)
            documents = serializers.EncryptedRecordDocumentSerializer(e_record.e_record_documents, many=True)
            messages = serializers.EncryptedRecordMessageSerializer(e_record.e_record_messages,
                                                                    many=True).get_decrypted_data(record_key)
            return Response({
                'record': record_data,
                'client': client_serializer,
                'origin_country': origin_country.data,
                'record_documents': documents.data,
                'record_messages': messages
            })
        else:
            serializer = serializers.EncryptedRecordNoDetailSerializer(e_record)
            permission_request = models.EncryptedRecordPermission.objects.filter(record=e_record, request_from=user,
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
        e_record = models.EncryptedRecord.objects.get(pk=id)
        user = request.user
        if user.rlc != e_record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if not e_record.user_has_permission(user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        record_data = request.data['record']
        client_data = request.data['client']
        client = e_record.client

        users_private_key = get_private_key_from_request(request)
        record_key = e_record.get_decryption_key(user, users_private_key)

        try:
            e_record.record_token = record_data['token']
            e_record.last_contact_date = parse_date(record_data['last_contact_date'])
            e_record.state = record_data['state']
            e_record.official_note = record_data['official_note']

            e_record.note = AESEncryption.encrypt(record_data['note'], record_key)
            e_record.consultant_team = AESEncryption.encrypt(record_data['consultant_team'], record_key)
            e_record.lawyer = AESEncryption.encrypt(record_data['lawyer'], record_key)
            e_record.related_persons = AESEncryption.encrypt(record_data['related_persons'], record_key)
            e_record.contact = AESEncryption.encrypt(record_data['contact'], record_key)
            e_record.bamf_token = AESEncryption.encrypt(record_data['bamf_token'], record_key)
            e_record.foreign_token = AESEncryption.encrypt(record_data['foreign_token'], record_key)
            e_record.first_correspondence = AESEncryption.encrypt(record_data['first_correspondence'], record_key)
            e_record.circumstances = AESEncryption.encrypt(record_data['circumstances'], record_key)
            e_record.next_steps = AESEncryption.encrypt(record_data['next_steps'], record_key)
            e_record.status_described = AESEncryption.encrypt(record_data['status_described'], record_key)
            e_record.additional_facts = AESEncryption.encrypt(record_data['additional_facts'], record_key)

            e_record.tagged.clear()
            for tag in record_data['tags']:
                e_record.tagged.add(models.RecordTag.objects.get(pk=tag['id']))
            client.birthday = parse_date(client_data['birthday'])
            client.origin_country = models.OriginCountry.objects.get(pk=client_data['origin_country'])

            rlcs_private_key = user.get_rlcs_private_key(users_private_key)
            client_key = e_record.client.get_password(rlcs_private_key)

            client.note = AESEncryption.encrypt(client_data['note'], client_key)
            client.name = AESEncryption.encrypt(client_data['name'], client_key)
            client.phone_number = AESEncryption.encrypt(client_data['phone_number'], client_key)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__COULD_NOT_SAVE)

        e_record.last_edited = datetime.utcnow().replace(tzinfo=pytz.utc)
        e_record.save()
        client.last_edited = datetime.utcnow().replace(tzinfo=pytz.utc)
        client.save()

        if not settings.DEBUG:
            record_url = FrontendLinks.get_record_link(e_record)
            for user in e_record.working_on_record.all():
                EmailSender.send_email_notification([user.email], "Patched Record",
                                                    "RLC Intranet Notification - A record of yours was changed. Look here:" +
                                                    record_url)
        record_from_db = models.EncryptedRecord.objects.get(pk=e_record.id)
        client_from_db = models.EncryptedClient.objects.get(pk=client.id)
        return Response(
            {
                'record': serializers.EncryptedRecordFullDetailSerializer(record_from_db).get_decrypted_data(
                    record_key),
                'client': serializers.EncryptedClientSerializer(client_from_db).get_decrypted_data(client_key)
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
