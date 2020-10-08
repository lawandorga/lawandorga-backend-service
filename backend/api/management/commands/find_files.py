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

import os
from django.core.management.base import BaseCommand

from backend.recordmanagement.models import RecordDocument
from backend.static.encrypted_storage import EncryptedStorage


class Command(BaseCommand):
    def handle(self, *args, **options):
        documents = RecordDocument.objects.all()
        successes = 0
        errors = 0
        for document in documents:
            print("document: ", document)
            s3_path = document.get_file_key()
            print("download from: ", s3_path)
            local_path = os.path.join("temp", document.name)
            print("to: ", local_path)
            try:
                EncryptedStorage.download_file_from_s3(s3_path, local_path)
                print("file successfully downloaded")
                os.remove(local_path)
                print("file deleted")
                successes = successes + 1
            except:
                print("error at downloading file, not found probably")
                errors = errors + 1
        if errors == 0:
            print("no errors, all files in database found on s3")
        else:
            print("there were some errors")
