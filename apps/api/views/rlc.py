from django.db.models import QuerySet
from rest_framework import mixins, viewsets

from apps.api.models.rlc import Rlc
from apps.api.serializers import RlcNameSerializer, RlcSerializer


class RlcViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Rlc.objects.all()
    serializer_class = RlcSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Rlc.objects.all().order_by("name")
        return queryset

    def get_authenticators(self):
        # self.action == 'list' would be better here but self.action is not set yet
        if self.request.path == "/api/rlcs/" and self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.action == "list":
            return []
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "list":
            return RlcNameSerializer
        return super().get_serializer_class()
