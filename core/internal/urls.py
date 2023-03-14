from django.urls import include, path

from . import api

urlpatterns = [
    path("pages/", include(api.pages_router.urls)),
    path("articles/", include(api.articles_router.urls)),
]
