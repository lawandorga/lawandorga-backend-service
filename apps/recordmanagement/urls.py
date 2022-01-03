from apps.recordmanagement.views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register("deletions", RecordDeletionViewSet)
router.register("oldrecords", EncryptedRecordViewSet)
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
    path("record_pool/", RecordPoolViewSet.as_view()),
    path("statistics/", RecordStatisticsViewSet.as_view(), ),
]
