from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.fields import empty

from core.models import CollabDocument, TextDocumentVersion


class CollabDocumentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    root = serializers.BooleanField(read_only=True)  # type: ignore

    class Meta:
        model = CollabDocument
        fields = "__all__"

    def validate_name(self, value):
        value = "".join(
            e
            for e in value
            if e.isalnum() or e in [" ", ".", ":", "*", "(", ")", "[", "]"]
        )
        return value


class CollabDocumentPathSerializer(CollabDocumentSerializer):
    class Meta:
        model = CollabDocument
        fields = ["path", "id"]


class CollabDocumentCreateSerializer(CollabDocumentSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        # super
        attrs = super().validate(attrs)
        # permission
        if not CollabDocument.user_has_permission_write(
            attrs["path"], self.context["request"].user
        ):
            raise ValidationError(
                "You don't have the necessary permission to create a document in this place."
            )
        # check path exists
        if (
            attrs["path"] != "/"
            and not CollabDocument.objects.filter(
                rlc=attrs["rlc"], path=attrs["path"][:-1]
            ).exists()
        ):
            raise ValidationError({"path": "This path does not exist."})
        # set new path
        attrs["path"] = attrs["path"] + attrs["name"]
        del attrs["name"]
        # check path is not a duplicate
        if CollabDocument.objects.filter(rlc=attrs["rlc"], path=attrs["path"]).exists():
            raise ValidationError({"name": "A document with this name exists already."})
        # return
        return attrs

    def run_validation(self, data=empty):
        if data is not empty:
            data = data.copy()
            data["rlc"] = self.context["request"].user.rlc.pk
        return super().run_validation(data)

    def get_children(self, _):
        return []

    def create(self, validated_data):
        data = {"rlc": self.context["request"].user.rlc, **validated_data}
        instance = super().create(data)
        # create a text document
        version = TextDocumentVersion(quill=False, document=instance, content="")
        version.encrypt(request=self.context["request"])
        version.save()
        # return
        return instance


class CollabDocumentRetrieveSerializer(CollabDocumentSerializer):
    content_html = serializers.SerializerMethodField()
    quill = serializers.SerializerMethodField()

    def get_latest_version(self, obj):
        if not hasattr(self, "latest_version"):
            self.latest_version = obj.versions.order_by("-created").first()
            if self.latest_version is None:
                raise NotFound()
        return self.latest_version

    def get_content_html(self, obj):
        latest_version = self.get_latest_version(obj)
        latest_version.decrypt(request=self.context["request"])
        return latest_version.items

    def get_quill(self, obj):
        latest_version = self.get_latest_version(obj)
        return latest_version.quill


class CollabDocumentUpdateSerializer(CollabDocumentRetrieveSerializer):
    content = serializers.CharField(write_only=True)

    def update(self, instance, validated_data):
        # change name if different
        if instance.name != validated_data["name"]:
            instance = instance.change_name_and_save(validated_data["name"])
        # save the latest instance
        if "content" not in validated_data:
            return instance
        latest_version = instance.versions.order_by("-created").first()
        if (
            latest_version is not None
            and latest_version.created.date() == timezone.now().date()
        ):
            version = latest_version
            version.items = validated_data["content"]
            version.quill = False
        else:
            version = TextDocumentVersion(
                content=validated_data["content"], document=instance, quill=False
            )
        version.encrypt(request=self.context["request"])
        version.save()
        # return
        return instance


class CollabDocumentListSerializer(CollabDocumentSerializer):
    children = serializers.SerializerMethodField()

    def __init__(self, instance, *args, **kwargs):
        self.documents = instance
        super().__init__(*args, **kwargs)

    def get_children(self, instance):
        slashes = instance.path.count("/") + 1

        def filter_func(doc):
            return doc.path.startswith(instance.path) and doc.path.count("/") == slashes

        children = [doc.pk for doc in filter(filter_func, self.documents)]
        return children
