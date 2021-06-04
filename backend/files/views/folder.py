from backend.files.models.folder import Folder
from backend.static.permissions import PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
from backend.files.serializers import FileSerializer, FolderSerializer, FolderCreateSerializer, FolderPathSerializer, \
    PermissionForFolderNestedSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from backend.files.models.file import File
from rest_framework.response import Response
from backend.files.models import PermissionForFolder
from backend.api.models import Group
from rest_framework import viewsets, status


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.none()
    serializer_class = FolderSerializer

    def get_queryset(self):
        return Folder.objects.filter(rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ['create']:
            return FolderCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return FolderPathSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        instance = Folder.objects.get(parent=None, rlc=request.user.rlc)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True)
    def items(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        folders = []
        for folder in instance.child_folders.all():
            print(folder)
            print(folder.user_can_see_folder(user))
            if folder.user_can_see_folder(user):
                folders.append(folder)
        folder_data = FolderSerializer(folders, many=True).data

        files_data = []
        if instance.user_has_permission_read(user) or instance.user_has_permission_write(user):
            files = File.objects.filter(folder=instance)
            files_data = FileSerializer(files, many=True).data

        data = folder_data + files_data
        return Response(data)

    @action(detail=True)
    def permissions(self, request, *args, **kwargs):
        folder = self.get_object()

        groups = Group.objects.filter(from_rlc=request.user.rlc)

        parents = folder.get_all_parents()
        children = folder.get_all_children()

        from_above = PermissionForFolder.objects.filter(
            folder__in=parents, group_has_permission__in=groups
        )

        normal = PermissionForFolder.objects.filter(
            folder=folder, group_has_permission__in=groups
        )

        from_below = PermissionForFolder.objects.filter(
            folder__in=children, group_has_permission__in=groups
        )

        permissions = []
        permissions += PermissionForFolderNestedSerializer(from_above, from_direction='ABOVE', many=True).data
        permissions += PermissionForFolderNestedSerializer(normal, many=True).data
        permissions += PermissionForFolderNestedSerializer(from_below, from_direction='BELOW', many=True).data

        return Response(permissions)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['parent'].user_has_permission_write(request.user):
            raise PermissionDenied()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.child_folders.exists() or instance.files_in_folder.exists():
            data = {
                'detail': 'There are still items in this folder. It can not be deleted.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not instance.user_has_permission_write(request.user):
            raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
