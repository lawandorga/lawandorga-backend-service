from typing import Any
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.request import Request
from apps.api.errors import CustomError
from apps.api.models import HasPermission, Permission
from apps.api.serializers import OldHasPermissionSerializer
from apps.collab.models import CollabDocument, PermissionForCollabDocument, TextDocumentVersion
from apps.collab.serializers import (
    CollabDocumentSerializer,
    PermissionForCollabDocumentNestedSerializer,
    PermissionForCollabDocumentSerializer, TextDocumentVersionSerializer, CollabDocumentCreateSerializer,
    CollabDocumentListSerializer, TextDocumentVersionCreateSerializer,
)
from apps.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT
from apps.static.permissions import (
    PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
    PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
    PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
)


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
                        return True
                return False

            return [doc for doc in queryset if access(doc)]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if not CollabDocument.user_has_permission_write(self.get_object().path, request.user):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def latest(self, request, *args, **kwargs):
        instance = self.get_object()
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
        if not CollabDocument.user_has_permission_write(instance.path, request.user):
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

    @action(detail=True, methods=["get", "post"])
    def permissions(self, request: Request, pk: int):
        document = self.get_object()

        if not request.user.has_permission(
            PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        if request.method == "GET":

            permissions_direct = PermissionForCollabDocument.objects.filter(
                document__path=document.path
            )
            permissions_below = PermissionForCollabDocument.objects.filter(
                document__path__startswith="{}/".format(document.path),
            ).exclude(document__path=document.path)

            permissions_above = []
            parts = document.path.split("/")
            i = 0
            while True:
                current_path = ""
                for j in range(i + 1):
                    if current_path != "":
                        current_path += "/"
                    current_path += parts[j]
                as_list = list(
                    PermissionForCollabDocument.objects.filter(
                        document__path=current_path
                    ).exclude(document__path=document.path)
                )
                permissions_above += as_list
                i += 1
                if i >= parts.__len__() - 1:
                    break

            overall_permissions_strings = [
                PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
                PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
                PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
            ]
            overall_permissions = Permission.objects.filter(
                name__in=overall_permissions_strings
            )
            has_permissions_for_groups = HasPermission.objects.filter(
                permission__in=overall_permissions,
            )

            return_object = {
                "from_above": PermissionForCollabDocumentNestedSerializer(
                    permissions_above, many=True
                ).data,
                "from_below": PermissionForCollabDocumentNestedSerializer(
                    permissions_below, many=True
                ).data,
                "direct": PermissionForCollabDocumentNestedSerializer(
                    permissions_direct, many=True
                ).data,
                "general": OldHasPermissionSerializer(
                    has_permissions_for_groups, many=True
                ).data,
            }
            return Response(return_object)
        if request.method == "POST":
            try:
                permission_for_document = PermissionForCollabDocument.objects.create(
                    group_has_permission_id=request.data["group_id"],
                    permission_id=request.data["permission_id"],
                    document=document,
                )
            except Exception as e:
                raise CustomError("invalid arguments")

            return Response(
                PermissionForCollabDocumentSerializer(permission_for_document).data,
                status=201,
            )
