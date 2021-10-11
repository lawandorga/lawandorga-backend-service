from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.recordmanagement.models.record_tag import RecordTag, Tag
from apps.recordmanagement.serializers import RecordTagSerializer, TagSerializer
from rest_framework import viewsets, status


class RecordTagViewSet(viewsets.ModelViewSet):
    queryset = RecordTag.objects.all()
    serializer_class = RecordTagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.none()
    serializer_class = TagSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.records.count() != 0:
            raise ParseError('This tag is still used in some records. You need to remove it from those records before '
                             'you can delete it.')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Tag.objects.filter(rlc=self.request.user.rlc)
