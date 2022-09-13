from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("articles", views.ArticleViewSet)
router.register("pages/index", views.IndexPageViewSet)
router.register("pages/imprint", views.ImprintPageViewSet)
router.register("pages/toms", views.TomsPageViewSet)
router.register("pages/help", views.HelpPageViewSet)
router.register("roadmap-items", views.RoadmapItemViewSet)
