from apps.collab.serializers.permission_for_collab_document import PermissionForCollabDocumentSerializer, \
    PermissionForCollabDocumentAllNamesSerializer
from rest_framework.exceptions import PermissionDenied
from apps.api.static import PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from apps.collab.models import PermissionForCollabDocument
from rest_framework import mixins, status


class PermissionForCollabDocumentViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = PermissionForCollabDocument.objects.all()
    serializer_class = PermissionForCollabDocumentSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC):
            raise PermissionDenied()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance = PermissionForCollabDocument.objects.get(pk=serializer.data['id'])
        data = PermissionForCollabDocumentAllNamesSerializer(instance).data
        return Response(data=data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC):
            raise PermissionDenied()
        return super().destroy(request, *args, **kwargs)
