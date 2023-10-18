import mimetypes
from typing import cast

from django.db import IntegrityError
from django.http import FileResponse
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.viewsets import GenericViewSet

from core.data_sheets.models import (
    RecordEncryptedFileEntry,
    RecordEncryptedSelectEntry,
    RecordEncryptedStandardEntry,
    RecordMultipleEntry,
    RecordSelectEntry,
    RecordStandardEntry,
    RecordStateEntry,
    RecordStatisticEntry,
    RecordUsersEntry,
)
from core.data_sheets.serializers.record import (
    RecordEncryptedFileEntrySerializer,
    RecordEncryptedSelectEntrySerializer,
    RecordEncryptedStandardEntrySerializer,
    RecordMultipleEntrySerializer,
    RecordSelectEntrySerializer,
    RecordStandardEntrySerializer,
    RecordStateEntrySerializer,
    RecordStatisticEntrySerializer,
    RecordUsersEntrySerializer,
)
from core.folders.domain.repositiories.folder import FolderRepository
from core.seedwork.repository import RepositoryWarehouse


###
# Entry
###
class RecordEntryViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    EXISTS_ERROR_MESSAGE = (
        "Somebody has already filled this entry with data. Please reload the page."
    )

    def perform_create(self, serializer):
        try:
            instance = serializer.save()
        except IntegrityError:
            raise ParseError(self.EXISTS_ERROR_MESSAGE)
        instance.record.save()  # update record updated field
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.record.save()  # update record updated field
        return instance


class RecordEncryptedSelectEntryViewSet(RecordEntryViewSet):
    queryset = RecordEncryptedSelectEntry.objects.none()
    serializer_class = RecordEncryptedSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedSelectEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )


class RecordEncryptedFileEntryViewSet(RecordEntryViewSet):
    queryset = RecordEncryptedFileEntry.objects.none()
    serializer_class = RecordEncryptedFileEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedFileEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )

    @action(detail=True, methods=["get"])
    def download(self, request, *args, **kwargs):
        instance = self.get_object()
        private_key_user = request.user.get_private_key(request=request)
        file = instance.decrypt_file(
            private_key_user=private_key_user, user=request.user.rlc_user
        )
        response = FileResponse(
            file, content_type=mimetypes.guess_type(instance.get_value())[0]
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            instance.get_value()
        )
        return response


class RecordStandardEntryViewSet(RecordEntryViewSet):
    queryset = RecordStandardEntry.objects.none()
    serializer_class = RecordStandardEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStandardEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )


class RecordSelectEntryViewSet(RecordEntryViewSet):
    queryset = RecordSelectEntry.objects.none()
    serializer_class = RecordSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordSelectEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )


class RecordMultipleEntryViewSet(RecordEntryViewSet):
    queryset = RecordMultipleEntry.objects.none()
    serializer_class = RecordMultipleEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordMultipleEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )


class RecordStateEntryViewSet(RecordEntryViewSet):
    queryset = RecordStateEntry.objects.none()
    serializer_class = RecordStateEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStateEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )


class RecordUsersEntryViewSet(RecordEntryViewSet):
    queryset = RecordUsersEntry.objects.none()
    serializer_class = RecordUsersEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordUsersEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )

    def create_encryptions(self, share_keys, record, users):
        if share_keys:
            user = self.request.user.rlc_user
            assert record.folder_uuid is not None
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            folder = r.retrieve(user.org_id, record.folder_uuid)
            for u in users:
                if not folder.has_access(u):
                    folder.grant_access(u, user)
            r.save(folder)

    def perform_create(self, serializer):
        instance = super().perform_create(serializer)
        self.create_encryptions(
            instance.field.share_keys, instance.record, list(instance.value.all())
        )

    def perform_update(self, serializer):
        instance = super().perform_update(serializer)
        self.create_encryptions(
            instance.field.share_keys, instance.record, list(instance.value.all())
        )


class RecordEncryptedStandardEntryViewSet(RecordEntryViewSet):
    queryset = RecordEncryptedStandardEntry.objects.none()
    serializer_class = RecordEncryptedStandardEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedStandardEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )


class RecordStatisticEntryViewSet(RecordEntryViewSet):
    queryset = RecordStatisticEntry.objects.none()
    serializer_class = RecordStatisticEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStatisticEntry.objects.filter(
            record__template__rlc=self.request.user.rlc
        )
