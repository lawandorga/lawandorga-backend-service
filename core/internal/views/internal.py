from typing import List

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet

from core.models import HelpPage


class HelpPageSerializer(ModelSerializer):
    class Meta:
        model = HelpPage
        fields = "__all__"


class PageViewSet(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().model.get_solo()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class HelpPageViewSet(PageViewSet):
    queryset = HelpPage.objects.none()
    serializer_class = HelpPageSerializer
    permission_classes: List = []
    authentication_classes: List = []
