from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.core.models import (
    Article,
    HelpPage,
    ImprintPage,
    IndexPage,
    RoadmapItem,
    TomsPage,
)
from apps.core.serializers import (
    ArticleDetailSerializer,
    ArticleSerializer,
    HelpPageSerializer,
    IndexPageSerializer,
    RoadmapItemSerializer,
    TomsPageSerializer,
)


class PageViewSet(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().model.get_solo()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class RoadmapItemViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = RoadmapItem.objects.all()
    serializer_class = RoadmapItemSerializer
    permission_classes = []
    authentication_classes = []


class ArticleViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = []
    authentication_classes = []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return super().get_serializer_class()


class IndexPageViewSet(PageViewSet):
    queryset = IndexPage.objects.none()
    serializer_class = IndexPageSerializer
    permission_classes = []
    authentication_classes = []


class ImprintPageViewSet(PageViewSet):
    queryset = ImprintPage.objects.none()
    serializer_class = IndexPageSerializer
    permission_classes = []
    authentication_classes = []


class TomsPageViewSet(PageViewSet):
    queryset = TomsPage.objects.none()
    serializer_class = TomsPageSerializer
    permission_classes = []
    authentication_classes = []


class HelpPageViewSet(PageViewSet):
    queryset = HelpPage.objects.none()
    serializer_class = HelpPageSerializer
    permission_classes = []
    authentication_classes = []
