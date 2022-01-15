from rest_framework.viewsets import GenericViewSet
from apps.api.serializers import PermissionSerializer
from apps.api.models import Permission
from rest_framework import mixins


class PermissionViewSet(mixins.ListModelMixin, GenericViewSet):
    model = Permission
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
