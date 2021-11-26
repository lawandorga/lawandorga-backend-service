from rest_framework.exceptions import ValidationError
from apps.collab.models import CollabDocument
from rest_framework import serializers


class CollabDocumentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    root = serializers.BooleanField(read_only=True)

    class Meta:
        model = CollabDocument
        fields = "__all__"


class CollabDocumentPathSerializer(CollabDocumentSerializer):
    class Meta:
        model = CollabDocument
        fields = ['path', 'id']


class CollabDocumentCreateSerializer(CollabDocumentSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not CollabDocument.user_has_permission_write(attrs['path'], self.context['request'].user):
            raise ValidationError("You don't have the necessary permission to create a document in this place.")
        if attrs['path'] != '/' and not CollabDocument.objects.filter(rlc=self.context['request'].user.rlc,
                                                                      path=attrs['path'][:-1]).exists():
            raise ValidationError('This path does not exist.')
        attrs['path'] = attrs['path'] + attrs['name']
        attrs['creator'] = self.context['request'].user
        attrs['rlc'] = self.context['request'].user.rlc
        del attrs['name']
        return attrs

    def get_children(self, _):
        return []


class CollabDocumentListSerializer(CollabDocumentSerializer):
    children = serializers.SerializerMethodField()

    def __init__(self, instance, *args, **kwargs):
        self.documents = instance
        super().__init__(*args, **kwargs)

    def get_children(self, instance):
        slashes = instance.path.count('/') + 1

        def filter_func(doc):
            return doc.path.startswith(instance.path) and doc.path.count('/') == slashes

        children = [doc.pk for doc in filter(filter_func, self.documents)]
        return children
