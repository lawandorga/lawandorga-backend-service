from apps.recordmanagement.views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register("origin_countries", OriginCountryViewSet)
router.register("record_deletion_requests", EncryptedRecordDeletionRequestViewSet)
router.register("oldrecords", EncryptedRecordViewSet)
router.register("e_clients", EncryptedClientViewSet)
router.register('questionnairetemplates', QuestionnaireTemplateViewSet)
router.register('messages', MessageViewSet)
router.register('questionnaires', QuestionnaireViewSet)
router.register('questionnaire_answers', QuestionnaireAnswersViewSet)
router.register('questionnaire_fields', QuestionnaireFieldsViewSet)
router.register('questionnaire_files', QuestionnaireFilesViewSet)
router.register("pool_records", PoolRecordViewSet)
router.register("pool_consultants", PoolConsultantViewSet)
router.register("consultants", ConsultantViewSet)
router.register('record_documents', EncryptedRecordDocumentViewSet)
router.register('record_permission_requests', RecordPermissionRequestViewSet)
router.register('tags', TagViewSet)
# new
router.register('recordtemplates', RecordTemplateViewSet)
router.register('records', RecordViewSet)
# fields
router.register('recordstatefields', RecordStateFieldViewSet)
router.register('recordusersfields', RecordUsersFieldViewSet)
router.register('recordselectfields', RecordSelectFieldViewSet)
router.register('recordstandardfields', RecordStandardFieldViewSet)
router.register('recordmultiplefields', RecordMultipleFieldViewSet)
# encrypted
router.register('recordencryptedselectfields', RecordEncryptedSelectFieldViewSet)
router.register('recordencryptedfilefields', RecordEncryptedFileFieldViewSet)
router.register('recordencryptedstandardfields', RecordEncryptedStandardFieldViewSet)
# entries
router.register('recordstateentries', RecordStateEntryViewSet)
router.register('recordusersentries', RecordUsersEntryViewSet)
router.register('recordselectentries', RecordSelectEntryViewSet)
router.register('recordstandardentries', RecordStandardEntryViewSet)
router.register('recordmultipleentries', RecordMultipleEntryViewSet)
# encrypted
router.register('recordencryptedselectentries', RecordEncryptedSelectEntryViewSet)
router.register('recordencryptedfileentries', RecordEncryptedFileEntryViewSet)
router.register('recordencryptedstandardentries', RecordEncryptedStandardEntryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "process_record_deletion_request/",
        EncryptedRecordDeletionProcessViewSet.as_view(),
    ),
    path("record_pool/", RecordPoolViewSet.as_view()),
    path("statistics/", RecordStatisticsViewSet.as_view(), ),
]
