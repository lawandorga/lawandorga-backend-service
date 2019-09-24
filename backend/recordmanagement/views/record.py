#  rlcapp - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.api.models import UserProfile
from backend.recordmanagement import models, serializers
from backend.static import error_codes
from backend.static import permissions
from backend.static.date_utils import parse_date
from backend.static.emails import EmailSender
from backend.static.frontend_links import FrontendLinks


class RecordsListViewSet(viewsets.ViewSet):
    def list(self, request):
        """

        :param request:
        :return:
        """
        parts = request.query_params.get('search', '').split(' ')
        user = request.user

        if user.is_superuser:
            entries = models.Record.objects.all()
            for part in parts:
                consultants = UserProfile.objects.filter(name__icontains=part)
                entries = entries.filter(
                    Q(tagged__name__icontains=part) | Q(note__icontains=part) | Q(
                        working_on_record__in=consultants) | Q(record_token__icontains=part)).distinct()
            serializer = serializers.RecordFullDetailSerializer(entries, many=True)
            return Response(serializer.data)

        if not user.has_permission(permissions.PERMISSION_VIEW_RECORDS_RLC,
                                   for_rlc=user.rlc) and not user.has_permission(
            permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # entries = models.Record.objects.filter(from_rlc=user.rlc)
        entries = models.Record.objects.filter_by_rlc(user.rlc)
        for part in parts:
            consultants = UserProfile.objects.filter(name__icontains=part)
            entries = entries.filter(
                Q(tagged__name__icontains=part) | Q(note__icontains=part) | Q(
                    working_on_record__in=consultants) | Q(record_token__icontains=part)).distinct()

        records = []
        if user.has_permission(permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc):
            queryset = entries
            serializer = serializers.RecordFullDetailSerializer(queryset, many=True)
            records += serializer.data
        else:
            queryset = entries.get_full_access_records(user).distinct()
            serializer = serializers.RecordFullDetailSerializer(queryset, many=True)
            records += serializer.data

            queryset = entries.get_no_access_records(user)
            serializer = serializers.RecordNoDetailSerializer(queryset, many=True)
            records += serializer.data
        return Response(records)

    def create(self, request):
        """outdated"""
        rlc = request.user.rlc
        record = models.Record(client_id=request.data['client'], first_contact_date=request.data['first_contact_date'],
                               last_contact_date=request.data['last_contact_date'],
                               record_token=request.data['record_token'],
                               note=request.data['note'],
                               creator_id=request.user.id,
                               from_rlc_id=rlc.id)
        record.save()
        for tag_id in request.data['tagged']:
            record.tagged.add(models.RecordTag.objects.get(pk=tag_id))
        for user_id in request.data['working_on_record']:
            record.working_on_record.add(UserProfile.objects.get(pk=user_id))
        record.save()
        return Response(serializers.RecordFullDetailSerializer(record).data)

    def retrieve(self, request, pk=None):
        # TODO: deprecated?
        try:
            record = models.Record.objects.get(pk=pk)  # changed
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__DOCUMENT__NOT_FOUND)

        if request.user.rlc != record.from_rlc:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)
        if record.user_has_permission(request.user):
            serializer = serializers.RecordFullDetailSerializer(record)
        else:
            serializer = serializers.RecordNoDetailSerializer(record)
        return Response(serializer.data)


class RecordViewSet(APIView):
    def post(self, request):
        if not request.user.has_permission(permissions.PERMISSION_CAN_ADD_RECORD_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        data = request.data
        rlc = request.user.rlc
        if 'client_id' in data:
            try:
                client = models.Client.objects.get(pk=data['client_id'])
            except:
                raise CustomError(error_codes.ERROR__RECORD__CLIENT__NOT_EXISTING)
            client.note = data['client_note']
            client.phone_number = data['client_phone_number']
            client.save()
        else:
            client = models.Client(name=data['client_name'], phone_number=data['client_phone_number'],
                                   birthday=data['client_birthday'], note=data['client_note'], from_rlc=rlc)
            client.save()
        try:
            origin = models.OriginCountry.objects.get(pk=data['origin_country'])
        except:
            raise CustomError(error_codes.ERROR__RECORD__ORIGIN_COUNTRY__NOT_FOUND)
        client.origin_country = origin
        client.save()

        record = models.Record(client_id=client.id, first_contact_date=data['first_contact_date'],
                               last_contact_date=data['first_contact_date'], record_token=data['record_token'],
                               note=data['record_note'], creator_id=request.user.id, from_rlc_id=rlc.id, state="op")
        record.save()

        for tag_id in data['tags']:
            record.tagged.add(models.RecordTag.objects.get(pk=tag_id))
        for user_id in data['consultants']:
            record.working_on_record.add(UserProfile.objects.get(pk=user_id))
        record.save()

        for user_id in data['consultants']:
            actual_consultant = UserProfile.objects.get(pk=user_id)
            url = FrontendLinks.get_record_link(record)
            EmailSender.send_email_notification([actual_consultant.email], "New Record",
                                                "RLC Intranet Notification - Your were assigned as a consultant for a new record. Look here:" +
                                                url)

        return Response(serializers.RecordFullDetailSerializer(record).data)

    def get(self, request, id):
        try:
            record = models.Record.objects.get(pk=id)
        except:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        user = request.user
        if user.rlc != record.from_rlc and not user.is_superuser:
            raise CustomError(error_codes.ERROR__RECORD__RETRIEVE_RECORD__WRONG_RLC)

        if record.user_has_permission(user):
            record_serializer = serializers.RecordFullDetailSerializer(record)
            client_serializer = serializers.ClientSerializer(record.client)
            origin_country = serializers.OriginCountrySerializer(record.client.origin_country)
            documents = serializers.RecordDocumentSerializer(record.record_documents, many=True)
            messages = serializers.RecordMessageSerializer(record.record_messages, many=True)

            return Response({
                'record': record_serializer.data,
                'client': client_serializer.data,
                'origin_country': origin_country.data,
                'record_documents': documents.data,
                'record_messages': messages.data
            })
        else:
            serializer = serializers.RecordNoDetailSerializer(record)
            permission_request = models.RecordPermission.objects.filter(record=record, request_from=user,
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
        except:
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

        pass
