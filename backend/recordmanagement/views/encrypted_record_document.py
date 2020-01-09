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
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from datetime import datetime
from threading import Thread

from backend.recordmanagement import models, serializers
from backend.shared import storage_generator
from backend.static import error_codes, storage_folders
from backend.api.errors import CustomError
from backend.static.encryption import AESEncryption
from backend.static.encrypted_storage import EncryptedStorage


class EncryptedRecordDocumentViewSet(viewsets.ModelViewSet):
    queryset = models.EncryptedRecordDocument.objects.all()
    serializer_class = serializers.EncryptedRecordDocumentSerializer

    def post(self, request):
        pass


class EncryptedRecordDocumentUploadViewSet(APIView):
    parser_classes = [FileUploadParser]

    def put(self, request, filename):
        file_obj = request.data['file']
        file_path = os.path.join('temp', filename)
        file = open(file_path, 'wb')
        if file_obj.multiple_chunks():
            for chunk in file_obj.chunks():
                file.write(chunk)
        else:
            file.write(file_obj.read())
            file.close()
        iv = os.urandom(16)
        self.encrypt_and_send_to_s3(file_path, 'asdasd', iv, 'tests') #  TODO: ! encryption
        return Response(status=204)


class EncryptedRecordDocumentByRecordViewSet(APIView):
    def get(self, request, id):
        pass

    def post(self, request, id):
        # TODO: ! encryption
        filename = request.data['filename']
        try:
            e_record = models.EncryptedRecord.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)

        if not e_record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        directory = storage_folders.get_storage_folder_encrypted_record_document(e_record.from_rlc_id, e_record.id)
        information = storage_generator.check_file_and_get_information(directory, filename)
        if 'error' in information:
            return Response(information)

        already_existing = models.RecordDocument.objects.filter(name=information['key']).first()
        if already_existing is not None:
            already_existing.file_size = information['size']
            already_existing.last_edited = datetime.now()
            already_existing.save()

            serializer = serializers.RecordDocumentSerializer(already_existing)
            return Response(serializer.data)
        else:
            name = information['key'].split('/')[-1]
            new_document = models.RecordDocument(record=e_record, name=name, creator=request.user,
                                                 file_size=information['size'])
            new_document.save()

            serializer = serializers.RecordDocumentSerializer(new_document)
            return Response(serializer.data)


class EncryptedRecordDocumentDownloadAllViewSet(APIView):
    def get(self, request, id):
        # TODO: ! encryption
        try:
            record = models.Record.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)

        if not record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        docs = list(models.RecordDocument.objects.filter(record=record))
        filenames = []
        for doc in docs:
            storage_generator.download_file(doc.get_filekey(), doc.name)
            filenames.append(doc.name)

        return storage_generator.zip_files_and_create_response(filenames, 'record.zip')
