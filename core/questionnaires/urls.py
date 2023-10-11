from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.questionnaires import api

router = DefaultRouter()


urlpatterns = [
    path("questionnaires/v2/", include(api.questionnaire_router.urls)),
    path("query/", include(api.query_router.urls)),
    path("templates/", include(api.templates_router.urls)),
    path("", include(router.urls)),
]
