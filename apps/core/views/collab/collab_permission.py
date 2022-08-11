from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.core.models import CollabPermission
from apps.core.serializers import CollabPermissionSerializer


class CollabPermissionViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = CollabPermission.objects.all()
    serializer_class = CollabPermissionSerializer
