from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from apps.collab.serializers import CollabDocumentSerializer, \
    TextDocumentVersionSerializer, CollabDocumentCreateSerializer, \
    CollabDocumentListSerializer, TextDocumentVersionCreateSerializer, PermissionForCollabDocumentAllNamesSerializer
from apps.api.static import PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC, \
    PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC, PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC
from rest_framework.response import Response
from rest_framework.request import Request
from apps.collab.models import CollabDocument, PermissionForCollabDocument, TextDocumentVersion
from rest_framework import viewsets, status
from typing import Any


class CollabDocumentViewSet(viewsets.ModelViewSet):
    queryset = CollabDocument.objects.none()
    serializer_class = CollabDocumentSerializer

    def get_serializer_class(self):
        if self.action in ['create']:
            return CollabDocumentCreateSerializer
        elif self.action in ['list']:
            return CollabDocumentListSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = CollabDocument.objects.filter(rlc=self.request.user.rlc)
        if (
            self.request.user.has_permission(PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC)
            or self.request.user.has_permission(PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC)
            or self.request.user.has_permission(PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC)
        ):
            return queryset
        else:
            queryset = list(queryset)
            permissions = list(self.request.user.get_collab_permissions())

            def access(doc):
                for permission in permissions:
                    permission_path = permission.document.path
                    if doc.path.startswith(permission_path):
                        # this means the user can 'access' the document and its content
                        return True
                    if permission.document.path.startswith(doc.path):
                        # this means the user can 'see' the document but not its content
                        return True
                return False

            return CollabDocument.objects.filter(pk__in=[doc for doc in queryset if access(doc)])

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        if not instance.user_can_write(request.user):
            raise PermissionDenied()
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def latest(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.user_can_read(request.user):
            raise PermissionDenied()
        versions = instance.versions.all()
        latest_version = versions.order_by('-created').first()
        if latest_version is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        latest_version.decrypt(
            request.user.rlc.get_aes_key(user=request.user,
                                         private_key_user=request.user.get_private_key(request=request)))
        return Response(TextDocumentVersionSerializer(latest_version).data)

    @action(detail=True, methods=['post'])
    def create_version(self, request, *args, **kwargs):
        # get the collab document
        instance = self.get_object()

        # check permissions
        if not instance.user_can_write(request.user):
            raise PermissionDenied()

        # check if data is valid
        serializer = TextDocumentVersionCreateSerializer(
            data={'content': request.data['content'], 'quill': False, 'document': instance.pk})
        serializer.is_valid(raise_exception=True)

        # get the keys
        private_key_user = request.user.get_private_key(request=request)
        aes_key_rlc = request.user.get_rlc_aes_key(private_key_user=private_key_user)

        # encrypt and save
        version = TextDocumentVersion(**serializer.validated_data)
        version.encrypt(aes_key_rlc)
        version.save()

        # return
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def versions(self, request, *args, **kwargs):
        instance = self.get_object()
        aes_key_rlc = request.user.get_rlc_aes_key(private_key_user=request.user.get_private_key(request=request))
        versions = list(instance.versions.all())
        for version in versions:
            version.decrypt(aes_key_rlc)
        serializer = TextDocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def permissions(self, request, *args, **kwargs):
        instance = self.get_object()

        normal = []
        from_below = []
        from_above = []
        for permission in PermissionForCollabDocument.objects \
            .filter(group_has_permission__in=request.user.rlc.group_from_rlc.all()) \
            .select_related('group_has_permission', 'document'):
            permission_path = permission.document.path
            if instance.has_permission_from_parent(permission_path):
                from_above.append(permission)
            if instance.has_permission_direct(permission_path):
                normal.append(permission)
            if instance.has_permission_from_below(permission_path):
                from_below.append(permission)

        permissions = []
        permissions += PermissionForCollabDocumentAllNamesSerializer(normal, from_direction='NORMAL', many=True).data
        permissions += PermissionForCollabDocumentAllNamesSerializer(from_below, from_direction='BELOW', many=True).data
        permissions += PermissionForCollabDocumentAllNamesSerializer(from_above, from_direction='ABOVE',
                                                                     many=True).data

        return Response(permissions)
