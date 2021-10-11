from apps.recordmanagement.models.record_document_tag import RecordDocumentTag
from apps.recordmanagement import serializers
from rest_framework import viewsets


class RecordDocumentTagViewSet(viewsets.ModelViewSet):
    queryset = RecordDocumentTag.objects.all()
    serializer_class = serializers.RecordDocumentTagSerializer
