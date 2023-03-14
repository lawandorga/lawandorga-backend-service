from typing import List

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Article, HelpPage

from ..serializers import (
    ArticleDetailSerializer,
    ArticleSerializer,
    HelpPageSerializer,
)


class PageViewSet(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().model.get_solo()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ArticleViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes: List = []
    authentication_classes: List = []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return super().get_serializer_class()


class HelpPageViewSet(PageViewSet):
    queryset = HelpPage.objects.none()
    serializer_class = HelpPageSerializer
    permission_classes: List = []
    authentication_classes: List = []
