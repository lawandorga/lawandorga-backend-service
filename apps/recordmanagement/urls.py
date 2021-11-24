from apps.recordmanagement.views.questionnaire import QuestionnaireViewSet, RecordQuestionnaireViewSet
from apps.recordmanagement.views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register("origin_countries", OriginCountryViewSet)
router.register("record_deletion_requests", EncryptedRecordDeletionRequestViewSet)
router.register("records", EncryptedRecordViewSet)
router.register("e_clients", EncryptedClientViewSet)
router.register('questionnaires', QuestionnaireViewSet)
router.register('record_questionnaires', RecordQuestionnaireViewSet)
router.register('questionnaire_answers', QuestionnaireAnswersViewSet)
router.register('questionnaire_fields', QuestionnaireFieldsViewSet)
router.register("pool_records", PoolRecordViewSet)
router.register("pool_consultants", PoolConsultantViewSet)
router.register("consultants", ConsultantViewSet)
router.register('record_documents', EncryptedRecordDocumentViewSet)
router.register('record_permission_requests', RecordPermissionRequestViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "process_record_deletion_request/",
        EncryptedRecordDeletionProcessViewSet.as_view(),
    ),
    path("record_pool/", RecordPoolViewSet.as_view()),
    path("statistics/", RecordStatisticsViewSet.as_view(), ),
]
