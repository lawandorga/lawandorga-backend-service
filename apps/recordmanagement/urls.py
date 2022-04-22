from apps.recordmanagement.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('records/messages', MessageViewSet)
router.register("records/pool_records", PoolRecordViewSet)
router.register("records/pool_consultants", PoolConsultantViewSet)
router.register('records/record_documents', EncryptedRecordDocumentViewSet)
# record access and deletion
router.register("records/deletions", RecordDeletionViewSet)
router.register('records/accesses', RecordAccessViewSet)
# questionnaires
router.register('records/questionnairetemplates', QuestionnaireTemplateViewSet)
router.register('records/questionnaires', QuestionnaireViewSet)
router.register('records/questionnaire_answers', QuestionnaireAnswersViewSet)
router.register('records/questionnaire_fields', QuestionnaireFieldsViewSet)
router.register('records/questionnaire_files', QuestionnaireFilesViewSet)
# records
router.register('records/recordtemplates', RecordTemplateViewSet)
router.register('records/records', RecordViewSet)
# encryptions
router.register('records/encryptions', RecordEncryptionNewViewSet)
# fields
router.register('records/recordstatefields', RecordStateFieldViewSet)
router.register('records/recordusersfields', RecordUsersFieldViewSet)
router.register('records/recordselectfields', RecordSelectFieldViewSet)
router.register('records/recordstandardfields', RecordStandardFieldViewSet)
router.register('records/recordmultiplefields', RecordMultipleFieldViewSet)
# fields encrypted
router.register('records/recordencryptedselectfields', RecordEncryptedSelectFieldViewSet)
router.register('records/recordencryptedfilefields', RecordEncryptedFileFieldViewSet)
router.register('records/recordencryptedstandardfields', RecordEncryptedStandardFieldViewSet)
# entries
router.register('records/recordstateentries', RecordStateEntryViewSet)
router.register('records/recordusersentries', RecordUsersEntryViewSet)
router.register('records/recordselectentries', RecordSelectEntryViewSet)
router.register('records/recordstandardentries', RecordStandardEntryViewSet)
router.register('records/recordmultipleentries', RecordMultipleEntryViewSet)
# entries encrypted
router.register('records/recordencryptedselectentries', RecordEncryptedSelectEntryViewSet)
router.register('records/recordencryptedfileentries', RecordEncryptedFileEntryViewSet)
router.register('records/recordencryptedstandardentries', RecordEncryptedStandardEntryViewSet)
# statistic
router.register('records/recordstatisticentries', RecordStatisticEntryViewSet)
