from apps.collab.models import TextDocumentVersion
from rest_framework import serializers


class TextDocumentVersionSerializer(serializers.ModelSerializer):
    content = serializers.CharField(allow_blank=True)

    class Meta:
        model = TextDocumentVersion
        fields = "__all__"


class TextDocumentVersionCreateSerializer(TextDocumentVersionSerializer):
    class Meta:
        model = TextDocumentVersion
        fields = ['document', 'content', 'quill']
