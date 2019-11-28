#  law&orga - record and organization management software for refugee law clinics
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
from backend.api.models import UserProfile


class RecordDeletionRequest(models.Model):
    record = models.ForeignKey('Record', related_name="deletions_requested", on_delete=models.CASCADE, null=False)
    request_from = models.OneToOneField(UserProfile, on_delete=models.SET_NULL, null=True)
    request_processed = models.ForeignKey(UserProfile, related_name="record_deletion_request_processed",
                                          on_delete=models.SET_NULL, null=True)
    explanation = models.CharField(max_length=4096)
    requested = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True)

    record_deletion_request_states_possible = (
        ('re', 'requested'),
        ('gr', 'granted'),
        ('de', 'declined')
    )
    state = models.CharField(max_length=2, choices=record_deletion_request_states_possible, default='re')
