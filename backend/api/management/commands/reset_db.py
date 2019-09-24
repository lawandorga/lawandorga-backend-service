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

from django.core.management.base import BaseCommand

from backend.api.models import *
from backend.recordmanagement.models import *


class Command(BaseCommand):
    help = 'resets database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        UserProfile.objects.exclude(is_superuser=True).delete()
        # UserProfile.objects.all().delete()
        Client.objects.all().delete()
        OriginCountry.objects.all().delete()
        RecordTag.objects.all().delete()
        Record.objects.all().delete()
        Group.objects.all().delete()
        HasPermission.objects.all().delete()
        Permission.objects.all().delete()
        Rlc.objects.all().delete()
        RecordMessage.objects.all().delete()
        RecordDocument.objects.all().delete()
        RecordDocumentTag.objects.all().delete()
        RecordPermission.objects.all().delete()
        ForgotPasswordLinks.objects.all().delete()
        Language.objects.all().delete()
        NewUserRequest.objects.all().delete()
        UserActivationLink.objects.all().delete()
