from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from apps.files.serializers import FileSerializer, FileCreateSerializer
from apps.files.models.file import File
from rest_framework import viewsets, status
from django.http import FileResponse
import mimetypes


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return FileCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_read(request.user):
            raise PermissionDenied()

        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlc_aes_key(private_key_user)
        file = instance.download(aes_key)

        response = FileResponse(file, content_type=mimetypes.guess_type(instance.key)[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        # delete the file again if there was no permission to write to the folder
        if not self.instance.folder.user_has_permission_write(request.user):
            self.instance.delete()
            raise PermissionDenied()

        # upload the file
        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlc_aes_key(private_key_user=private_key_user)
        file = request.FILES.get('file')
        self.instance.upload(file, aes_key)
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_write(request.user):
            raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
