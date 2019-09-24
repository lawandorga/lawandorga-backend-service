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

from django.db import models
from django.db.models import Q

from backend.api.models import UserProfile, Rlc
from backend.recordmanagement.models import RecordTag
from backend.static import permissions


class RecordQuerySet(models.QuerySet):
    def get_full_access_records(self, user):
        from backend.recordmanagement.models import RecordPermission
        permissions = RecordPermission.objects.filter(request_from=user, state='gr')

        return self.filter(Q(id__in=user.working_on_record.values_list('id', flat=True)) | Q(
            id__in=permissions.values_list('record_id', flat=True)))

    def get_no_access_records(self, user):
        # permissions = RecordPermission.objects.filter(request_from=user, state='gr')
        # return self.exclude(Q(id__in=user.working_on_record.values_list('id', flat=True)) | Q(
        #     id__in=permissions.values_list('record_id', flat=True)))
        has_perm = self.get_full_access_records(user)
        return self.exclude(id__in=has_perm.values_list('id', flat=True))

    def filter_by_rlc(self, rlc):
        """
        filters by the instance of the given rlc
        :param rlc: instance of rlc
        :return: filtered values
        """
        return self.filter(from_rlc=rlc)


class Record(models.Model):
    creator = models.ForeignKey(
        UserProfile, related_name="records_created", on_delete=models.SET_NULL, null=True)
    from_rlc = models.ForeignKey(Rlc, related_name='record_from_rlc', on_delete=models.SET_NULL, null=True,
                                 default=None)

    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    client = models.ForeignKey(
        'Client', related_name="records", on_delete=models.SET_NULL, null=True)
    first_contact_date = models.DateField(default=None, null=True)
    last_contact_date = models.DateTimeField(default=None, null=True)
    first_consultation = models.DateTimeField(default=None, null=True)

    record_token = models.CharField(
        max_length=50, unique=True)
    note = models.TextField(blank=True, null=True)
    official_note = models.TextField(blank=True, null=True)

    consultant_team = models.CharField(max_length=255, blank=True, null=True)
    lawyer = models.TextField(blank=True, null=True)
    related_persons = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)

    bamf_token = models.CharField(max_length=255)
    foreign_token = models.CharField(max_length=255)

    first_correspondence = models.TextField(blank=True, null=True)
    circumstances = models.TextField(blank=True, null=True)
    next_steps = models.TextField(blank=True, null=True)
    status_described = models.TextField(blank=True, null=True)
    additional_facts = models.TextField(blank=True, null=True)

    working_on_record = models.ManyToManyField(
        UserProfile, related_name="working_on_record", blank=True)
    tagged = models.ManyToManyField(RecordTag, related_name="tagged", blank=True)

    record_states_possible = (
        ('op', 'open'),
        ('cl', 'closed'),
        ('wa', 'waiting'),
        ('wo', 'working')
    )

    state = models.CharField(max_length=2, choices=record_states_possible)

    objects = RecordQuerySet.as_manager()

    def __str__(self):
        return 'record: ' + str(self.id) + ':' + self.record_token

    def user_has_permission(self, user):
        """
        return if the user has permission edit and view the record in full detail
        :param user: user object, the user to check
        :return: boolean, true if the user has permission
        """
        from backend.recordmanagement.models import RecordPermission
        return self.working_on_record.filter(id=user.id).count() == 1 or \
               RecordPermission.objects.filter(record=self, request_from=user, state='gr') or \
               user.has_permission(permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc)

    def get_notification_emails(self):
        from backend.recordmanagement.models import RecordPermission
        emails = []
        for user in list(self.working_on_record.all()):
            emails.append(user.email)
        for permission_request in list(RecordPermission.objects.filter(record=self, state='gr')):
            emails.append(permission_request.request_from.email)
        return emails

