from apps.recordmanagement.serializers.record import RecordTemplateSerializer, RecordEncryptedStandardFieldSerializer, \
    RecordFieldSerializer, RecordSerializer, RecordEncryptedStandardEntrySerializer, RecordStandardEntrySerializer, \
    RecordEncryptedFileEntrySerializer, RecordStandardFieldSerializer, RecordEncryptedFileFieldSerializer, \
    RecordEncryptedSelectFieldSerializer, RecordEncryptedSelectEntrySerializer, RecordUsersFieldSerializer, \
    RecordUsersEntrySerializer, RecordStateFieldSerializer, \
    RecordStateEntrySerializer, RecordSelectEntrySerializer, RecordSelectFieldSerializer, RecordListSerializer, \
    RecordDetailSerializer, RecordCreateSerializer, RecordMultipleEntrySerializer, RecordMultipleFieldSerializer
from apps.recordmanagement.models.record import RecordTemplate, RecordEncryptedStandardField, Record, \
    RecordEncryptionNew, RecordEncryptedStandardEntry, RecordStandardEntry, RecordEncryptedFileEntry, \
    RecordStandardField, RecordEncryptedFileField, \
    RecordEncryptedSelectField, RecordEncryptedSelectEntry, RecordUsersField, RecordUsersEntry, RecordStateField, \
    RecordStateEntry, RecordSelectEntry, RecordSelectField, RecordMultipleEntry, RecordMultipleField
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from apps.static.encryption import AESEncryption
from rest_framework import status, mixins


###
# Template
###
class RecordTemplateViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                            mixins.ListModelMixin, GenericViewSet):
    queryset = RecordTemplate.objects.none()
    serializer_class = RecordTemplateSerializer

    def get_queryset(self):
        return RecordTemplate.objects.filter(rlc=self.request.user.rlc)

    @action(detail=True, methods=['get'])
    def fields(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.fields.all()
        serializer = RecordFieldSerializer(queryset, many=True)
        return Response(serializer.data)


###
# Fields
###
class RecordStateFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordStateField.objects.none()
    serializer_class = RecordStateFieldSerializer

    def get_queryset(self):
        return RecordStateField.objects.filter(template__rlc=self.request.user.rlc)


class RecordEncryptedStandardFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                          GenericViewSet):
    queryset = RecordEncryptedStandardField.objects.none()
    serializer_class = RecordEncryptedStandardFieldSerializer

    def get_queryset(self):
        return RecordEncryptedStandardField.objects.filter(template__rlc=self.request.user.rlc)


class RecordStandardFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 GenericViewSet):
    queryset = RecordStandardField.objects.none()
    serializer_class = RecordStandardFieldSerializer

    def get_queryset(self):
        return RecordStandardField.objects.filter(template__rlc=self.request.user.rlc)


class RecordSelectFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                               GenericViewSet):
    queryset = RecordSelectField.objects.none()
    serializer_class = RecordSelectFieldSerializer

    def get_queryset(self):
        return RecordSelectField.objects.filter(template__rlc=self.request.user.rlc)


class RecordMultipleFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 GenericViewSet):
    queryset = RecordMultipleField.objects.none()
    serializer_class = RecordMultipleFieldSerializer

    def get_queryset(self):
        return RecordMultipleField.objects.filter(template__rlc=self.request.user.rlc)


class RecordEncryptedFileFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                      GenericViewSet):
    queryset = RecordEncryptedFileField.objects.none()
    serializer_class = RecordEncryptedFileFieldSerializer

    def get_queryset(self):
        return RecordEncryptedFileField.objects.filter(template__rlc=self.request.user.rlc)


class RecordEncryptedSelectFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                        GenericViewSet):
    queryset = RecordEncryptedSelectField.objects.none()
    serializer_class = RecordEncryptedSelectFieldSerializer

    def get_queryset(self):
        return RecordEncryptedSelectField.objects.filter(template__rlc=self.request.user.rlc)


class RecordUsersFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordUsersField.objects.none()
    serializer_class = RecordUsersFieldSerializer

    def get_queryset(self):
        return RecordUsersField.objects.filter(template__rlc=self.request.user.rlc)


###
# Record
###
class RecordViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                    GenericViewSet):
    queryset = Record.objects.none()
    serializer_class = RecordSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return RecordListSerializer
        elif self.action in ['retrieve']:
            return RecordDetailSerializer
        elif self.action in ['create']:
            return RecordCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ['list']:
            return Record.objects.filter(template__rlc=self.request.user.rlc).prefetch_related(
                'state_entries', 'state_entries__field',
                'select_entries', 'select_entries__field',
                'standard_entries', 'standard_entries__field',
                'users_entries', 'users_entries__value', 'users_entries__field',
                'multiple_entries', 'multiple_entries__field',
                'encryptions'
            ).select_related('template')
        elif self.action in ['retrieve']:
            return Record.objects.filter(template__rlc=self.request.user.rlc).prefetch_related(
                'state_entries', 'state_entries__field',
                'select_entries', 'select_entries__field',
                'standard_entries', 'standard_entries__field',
                'multiple_entries', 'multiple_entries__field',
                'users_entries', 'users_entries__field', 'users_entries__value',
                'encrypted_select_entries', 'encrypted_select_entries__field',
                'encrypted_standard_entries', 'encrypted_standard_entries__field',
                'encrypted_file_entries', 'encrypted_file_entries__field',
                'template',
                'template__standard_fields',
                'template__select_fields',
                'template__users_fields',
                'template__state_fields',
                'template__encrypted_file_fields',
                'template__encrypted_select_fields',
                'template__encrypted_standard_fields',
            ).select_related('old_client')
        return Record.objects.filter(template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        created_record = Record.objects.get(pk=response.data['id'])
        aes_key = AESEncryption.generate_secure_key()
        public_key_user = request.user.get_public_key()
        encryption = RecordEncryptionNew(record=created_record, user=request.user, key=aes_key)
        encryption.encrypt(public_key_user=public_key_user)
        encryption.save()
        return response


###
# Entry
###
class RecordEncryptedSelectEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                        GenericViewSet):
    queryset = RecordEncryptedSelectEntry.objects.none()
    serializer_class = RecordEncryptedSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedSelectEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        entry = RecordEncryptedSelectEntry(**serializer.validated_data)
        entry.encrypt(user=request.user, private_key_user=private_key_user)
        entry.save()
        serializer = self.get_serializer(instance=entry, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        self.instance = super().get_object()
        return self.instance

    def perform_update(self, serializer):
        for attr, value in serializer.validated_data.items():
            setattr(self.instance, attr, value)
        private_key_user = self.request.user.get_private_key(request=self.request)
        self.instance.encrypt(user=self.request.user, private_key_user=private_key_user)
        self.instance.save()
        self.instance.decrypt(user=self.request.user, private_key_user=private_key_user)


class RecordEncryptedFileEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                      GenericViewSet):
    queryset = RecordEncryptedFileEntry.objects.none()
    serializer_class = RecordEncryptedFileEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedFileEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordStandardEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 GenericViewSet):
    queryset = RecordStandardEntry.objects.none()
    serializer_class = RecordStandardEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStandardEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordSelectEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                               GenericViewSet):
    queryset = RecordSelectEntry.objects.none()
    serializer_class = RecordSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordSelectEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordMultipleEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 GenericViewSet):
    queryset = RecordMultipleEntry.objects.none()
    serializer_class = RecordMultipleEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordMultipleEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordStateEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordStateEntry.objects.none()
    serializer_class = RecordStateEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStateEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordUsersEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordUsersEntry.objects.none()
    serializer_class = RecordUsersEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordUsersEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordEncryptedStandardEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                          GenericViewSet):
    queryset = RecordEncryptedStandardEntry.objects.none()
    serializer_class = RecordEncryptedStandardEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedStandardEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        record = serializer.validated_data['record']
        aes_key_record = record.get_aes_key(request.user, private_key_user)
        entry = RecordEncryptedStandardEntry(**serializer.validated_data)
        entry.encrypt(aes_key_record=aes_key_record)
        entry.save()
        entry.decrypt(aes_key_record=aes_key_record)
        serializer = self.get_serializer(instance=entry, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        self.instance = super().get_object()
        return self.instance

    def perform_update(self, serializer):
        for attr, value in serializer.validated_data.items():
            setattr(self.instance, attr, value)
        private_key_user = self.request.user.get_private_key(request=self.request)
        aes_key_record = self.instance.record.get_aes_key(user=self.request.user, private_key_user=private_key_user)
        self.instance.encrypt(aes_key_record=aes_key_record)
        self.instance.save()
        self.instance.decrypt(user=self.request.user, aes_key_record=aes_key_record)
