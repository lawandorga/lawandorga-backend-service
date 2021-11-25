from rest_framework.response import Response

from apps.internal.serializers import ArticleSerializer, ArticleDetailSerializer, IndexPageSerializer, \
    RoadmapItemSerializer
from rest_framework.viewsets import GenericViewSet
from apps.internal.models import Article, IndexPage, RoadmapItem, ImprintPage
from rest_framework import mixins


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
        raise Exception()
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return super().get_serializer_class()


class IndexPageViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = IndexPage.objects.none()
    serializer_class = IndexPageSerializer
    permission_classes = []
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        instance = IndexPage.get_solo()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ImprintPageViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = ImprintPage.objects.none()
    serializer_class = IndexPageSerializer
    permission_classes = []
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        instance = ImprintPage.get_solo()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
