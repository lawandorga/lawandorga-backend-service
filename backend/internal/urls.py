from rest_framework.routers import DefaultRouter
from backend.internal import viewsets

router = DefaultRouter()
router.register("articles", viewsets.ArticleViewSet)
router.register("pages/index", viewsets.IndexPageViewSet)
