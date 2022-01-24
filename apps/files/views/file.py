from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from apps.files.serializers import FileSerializer, FileCreateSerializer, FileUpdateSerializer
from apps.files.models.file import File
from rest_framework import viewsets, status
from django.http import FileResponse
import mimetypes


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_serializer_class(self):
        if self.action in ['create']:
            return FileCreateSerializer
        elif self.action in ['partial_update']:
            return FileUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_read(request.user):
            raise PermissionDenied()

        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlc_aes_key(private_key_user)
        file = instance.decrypt_file(aes_key)

        response = FileResponse(file, content_type=mimetypes.guess_type(instance.key)[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        return response

    def create(self, request, *args, **kwargs):
        # create
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # return standard data
        serializer = FileSerializer(instance=File.objects.get(pk=self.instance.pk))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_write(request.user):
            raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        # get the file
        instance = self.get_object()
        # permission stuff
        if not instance.folder.user_has_permission_write(request.user):
            raise PermissionDenied()
        # update
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # return standard data
        serializer = FileSerializer(instance=File.objects.get(pk=instance.pk))
        return Response(serializer.data)
