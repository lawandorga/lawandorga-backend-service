from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

router.register("articles", views.ArticleViewSet)
router.register("pages/help", views.HelpPageViewSet)

urlpatterns = [
    path("pages/", include(api.pages_router.urls)),
]
