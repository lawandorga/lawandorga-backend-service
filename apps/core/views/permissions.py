from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.core.models import Permission
from apps.core.serializers import PermissionSerializer


class PermissionViewSet(mixins.ListModelMixin, GenericViewSet):
    model = Permission
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
