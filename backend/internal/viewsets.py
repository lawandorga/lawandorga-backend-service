from backend.internal.serializers import ArticleSerializer
from rest_framework.viewsets import GenericViewSet
from backend.internal.models import Article
from rest_framework import mixins


class ArticleViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = []
    authentication_classes = []

