from backend.recordmanagement.models.record_tag import RecordTag, Tag
from backend.recordmanagement.serializers import RecordTagSerializer, TagSerializer
from rest_framework import viewsets


class RecordTagViewSet(viewsets.ModelViewSet):
    queryset = RecordTag.objects.all()
    serializer_class = RecordTagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.none()
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(rlc=self.request.user.rlc)
