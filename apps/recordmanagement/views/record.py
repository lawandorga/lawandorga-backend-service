from apps.recordmanagement.serializers.record import RecordTemplateSerializer, RecordTextFieldSerializer, \
    RecordFieldSerializer, RecordSerializer, RecordTextEntrySerializer, RecordMetaEntrySerializer, \
    RecordFileEntrySerializer, RecordMetaFieldSerializer, RecordFileFieldSerializer, RecordSelectFieldSerializer, \
    RecordSelectEntrySerializer, RecordUsersFieldSerializer, RecordUsersEntrySerializer, RecordStateFieldSerializer, \
    RecordStateEntrySerializer
from apps.recordmanagement.models.record import RecordTemplate, RecordTextField, Record, \
    RecordEncryptionNew, RecordTextEntry, RecordMetaEntry, RecordFileEntry, RecordMetaField, RecordFileField, \
    RecordSelectField, RecordSelectEntry, RecordUsersField, RecordUsersEntry, RecordStateField, RecordStateEntry
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


class RecordTextFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = RecordTextField.objects.none()
    serializer_class = RecordTextFieldSerializer

    def get_queryset(self):
        return RecordTextField.objects.filter(template__rlc=self.request.user.rlc)


class RecordMetaFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = RecordMetaField.objects.none()
    serializer_class = RecordMetaFieldSerializer

    def get_queryset(self):
        return RecordMetaField.objects.filter(template__rlc=self.request.user.rlc)


class RecordFileFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = RecordFileField.objects.none()
    serializer_class = RecordFileFieldSerializer

    def get_queryset(self):
        return RecordFileField.objects.filter(template__rlc=self.request.user.rlc)


class RecordSelectFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                               GenericViewSet):
    queryset = RecordSelectField.objects.none()
    serializer_class = RecordSelectFieldSerializer

    def get_queryset(self):
        return RecordSelectField.objects.filter(template__rlc=self.request.user.rlc)


class RecordUsersFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordUsersField.objects.none()
    serializer_class = RecordUsersFieldSerializer

    def get_queryset(self):
        return RecordUsersField.objects.filter(template__rlc=self.request.user.rlc)


###
# Record
###
class RecordViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Record.objects.none()
    serializer_class = RecordSerializer

    def get_queryset(self):
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
class RecordSelectEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                               GenericViewSet):
    queryset = RecordSelectEntry.objects.none()
    serializer_class = RecordSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordSelectEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        entry = RecordSelectEntry(**serializer.validated_data)
        entry.encrypt(user=request.user, private_key_user=private_key_user)
        entry.save()
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


class RecordFileEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = RecordFileEntry.objects.none()
    serializer_class = RecordFileEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordFileEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordMetaEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = RecordMetaEntry.objects.none()
    serializer_class = RecordMetaEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordMetaEntry.objects.filter(record__template__rlc=self.request.user.rlc)


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


class RecordTextEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = RecordTextEntry.objects.none()
    serializer_class = RecordTextEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordTextEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        record = serializer.validated_data['record']
        aes_key_record = record.get_aes_key(request.user, private_key_user)
        entry = RecordTextEntry(**serializer.validated_data)
        entry.encrypt(aes_key_record=aes_key_record)
        entry.save()
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
