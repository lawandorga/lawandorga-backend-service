from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.questionnaires import api, views

router = DefaultRouter()

# questionnaires
# router.register("questionnairetemplates", views.QuestionnaireTemplateViewSet)
router.register("questionnaires", views.QuestionnaireViewSet)
router.register("questionnaire_answers", views.QuestionnaireAnswersViewSet)
# router.register("questionnaire_fields", views.QuestionnaireFieldsViewSet)
# router.register("questionnaire_files", views.QuestionnaireFilesViewSet)

urlpatterns = [
    path("questionnaires/v2/", include(api.questionnaire_router.urls)),
    path("query/", include(api.query_router.urls)),
    path("templates/", include(api.templates_router.urls)),
    path("", include(router.urls)),
]
