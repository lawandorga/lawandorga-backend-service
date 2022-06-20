from typing import Any

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.static import (
    PERMISSION_COLLAB_MANAGE_PERMISSIONS,
    PERMISSION_COLLAB_READ_ALL_DOCUMENTS,
    PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS,
)
from apps.collab.models import CollabDocument, PermissionForCollabDocument
from apps.collab.serializers import (
    CollabDocumentCreateSerializer,
    CollabDocumentListSerializer,
    CollabDocumentRetrieveSerializer,
    CollabDocumentSerializer,
    CollabDocumentUpdateSerializer,
    PermissionForCollabDocumentAllNamesSerializer,
    TextDocumentVersionSerializer,
)


class CollabDocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CollabDocument.objects.none()
    serializer_class = CollabDocumentSerializer

    def get_serializer_class(self):
        if self.action in ["create"]:
            return CollabDocumentCreateSerializer
        elif self.action in ["retrieve"]:
            return CollabDocumentRetrieveSerializer
        elif self.action in ["update", "partial_update"]:
            return CollabDocumentUpdateSerializer
        elif self.action in ["list"]:
            return CollabDocumentListSerializer
        return super().get_serializer_class()

    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    def get_queryset(self):
        queryset = CollabDocument.objects.filter(rlc=self.request.user.rlc)
        if (
            self.request.user.has_permission(PERMISSION_COLLAB_READ_ALL_DOCUMENTS)
            or self.request.user.has_permission(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)
            or self.request.user.has_permission(PERMISSION_COLLAB_MANAGE_PERMISSIONS)
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

            return CollabDocument.objects.filter(
                pk__in=[doc.pk for doc in queryset if access(doc)]
            )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        if not instance.user_can_write(request.user):
            raise PermissionDenied()
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.user_can_read(request.user):
            raise PermissionDenied()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # get the collab document
        instance = self.get_object()

        # check permissions
        if not instance.user_can_write(request.user):
            raise PermissionDenied()

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def versions(self, request, *args, **kwargs):
        instance = self.get_object()
        aes_key_rlc = request.user.get_rlc_aes_key(
            private_key_user=request.user.get_private_key(request=request)
        )
        versions = list(instance.versions.all())
        for version in versions:
            version.decrypt(aes_key_rlc)
        serializer = TextDocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def permissions(self, request, *args, **kwargs):
        instance = self.get_object()

        normal = []
        from_below = []
        from_above = []
        for permission in PermissionForCollabDocument.objects.filter(
            group_has_permission__in=request.user.rlc.group_from_rlc.all()
        ).select_related("group_has_permission", "document"):
            permission_path = permission.document.path
            if instance.has_permission_from_parent(permission_path):
                from_above.append(permission)
            if instance.has_permission_direct(permission_path):
                normal.append(permission)
            if instance.has_permission_from_below(permission_path):
                from_below.append(permission)

        permissions = []
        permissions += PermissionForCollabDocumentAllNamesSerializer(
            normal, from_direction="NORMAL", many=True
        ).data
        permissions += PermissionForCollabDocumentAllNamesSerializer(
            from_below, from_direction="BELOW", many=True
        ).data
        permissions += PermissionForCollabDocumentAllNamesSerializer(
            from_above, from_direction="ABOVE", many=True
        ).data

        return Response(permissions)
