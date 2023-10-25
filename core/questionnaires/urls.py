from django.urls import include, path

from core.questionnaires import api

urlpatterns = [
    path("questionnaires/v2/", include(api.questionnaire_router.urls)),
    path("query/", include(api.query_router.urls)),
]
