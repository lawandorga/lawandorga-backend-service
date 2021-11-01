from rest_framework.exceptions import ValidationError
from apps.collab.models import CollabDocument, UserProfile
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


class CollabDocumentPermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabDocument
        fields = "__all__"


class CollabDocumentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField("get_sub_tree")
    name = serializers.SerializerMethodField('get_name', read_only=True)

    def __init__(
        self,
        user: UserProfile,
        all_documents: [CollabDocument],
        overall_permission: bool,
        see_subfolders: bool,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user = user
        self.all_documents = all_documents
        self.overall_permission = overall_permission
        self.see_subfolders = see_subfolders

    class Meta:
        model = CollabDocument
        fields = (
            "pk",
            "path",
            "created",
            "creator",
            "children",
            "name"
        )

    def get_name(self, document):
        return document.path.split('/')[-1]

    def get_sub_tree(self, document: CollabDocument):
        child_documents = []
        for doc in self.all_documents:
            ancestor: bool = doc.path.startswith("{}/".format(document.path))
            direct_child: bool = "/" not in doc.path[len(document.path) + 1:]

            if ancestor and direct_child:
                subfolders = False
                if self.overall_permission or self.see_subfolders:
                    add = True
                else:
                    add, subfolders = doc.user_can_see(self.user)
                if add:
                    child_documents.append(
                        CollabDocumentTreeSerializer(
                            instance=doc,
                            user=self.user,
                            all_documents=self.all_documents,
                            see_subfolders=subfolders or self.see_subfolders,
                            overall_permission=self.overall_permission,
                        ).data
                    )
        return child_documents
