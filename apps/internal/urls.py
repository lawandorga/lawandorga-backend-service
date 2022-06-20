from rest_framework.routers import DefaultRouter

from apps.internal import viewsets

router = DefaultRouter()
router.register("articles", viewsets.ArticleViewSet)
router.register("pages/index", viewsets.IndexPageViewSet)
router.register("pages/imprint", viewsets.ImprintPageViewSet)
router.register("pages/toms", viewsets.TomsPageViewSet)
router.register("pages/help", viewsets.HelpPageViewSet)
router.register("roadmap-items", viewsets.RoadmapItemViewSet)
