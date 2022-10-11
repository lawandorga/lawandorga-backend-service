from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.core.records.models import EncryptedRecordMessage
from apps.core.records.serializers import (
    EncryptedRecordMessageDetailSerializer,
    EncryptedRecordMessageSerializer,
)


class MessageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = EncryptedRecordMessage.objects.none()
    serializer_class = EncryptedRecordMessageSerializer

    def get_queryset(self):
        queryset = self.queryset
        record = self.request.query_params.get("record")
        if record is not None:
            queryset = EncryptedRecordMessage.objects.filter(
                record__template__rlc=self.request.user.rlc, record_id=record
            )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        message = EncryptedRecordMessage(**serializer.validated_data)
        message.encrypt(user=request.user, private_key_user=private_key_user)
        message.save()
        message.decrypt(user=request.user, private_key_user=private_key_user)
        serializer = EncryptedRecordMessageDetailSerializer(
            instance=message, context={"request": request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request, *args, **kwargs):
        private_key_user = request.user.get_private_key(request=request)
        messages = self.filter_queryset(self.get_queryset())
        messages_data = []
        for message in list(messages):
            message.decrypt(user=request.user, private_key_user=private_key_user)
            messages_data.append(EncryptedRecordMessageDetailSerializer(message).data)
        return Response(messages_data)
