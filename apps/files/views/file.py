from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from apps.files.serializers import FileSerializer, FileCreateSerializer, FileUpdateSerializer
from apps.files.models.file import File
from rest_framework import status, mixins
from django.http import FileResponse
import mimetypes


class FileViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_serializer_class(self):
        if self.action in ['create']:
            return FileCreateSerializer
        elif self.action in ['partial_update']:
            return FileUpdateSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_read(request.user):
            raise PermissionDenied()

        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlc_aes_key(private_key_user)
        try:
            file = instance.decrypt_file(aes_key)
        except FileNotFoundError:
            instance.exists = False
            instance.save()
            raise NotFound('The file could not be found on the server. Please delete it or contact it@law-orga.de '
                           'to have it recovered.')

        response = FileResponse(file, content_type=instance.mimetype)
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        return response

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def create(self, request, *args, **kwargs):
        # create
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # return standard data
        serializer = FileSerializer(instance=File.objects.get(pk=self.instance.pk))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_write(request.user):
            raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
