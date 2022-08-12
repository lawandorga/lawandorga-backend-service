from rest_framework.routers import DefaultRouter

from apps.recordmanagement import views

router = DefaultRouter()

router.register("records/messages", views.MessageViewSet)
router.register("records/pool_records", views.PoolRecordViewSet)
router.register("records/pool_consultants", views.PoolConsultantViewSet)
router.register("records/record_documents", views.EncryptedRecordDocumentViewSet)
# record access and deletion
router.register("records/deletions", views.RecordDeletionViewSet)
router.register("records/accesses", views.RecordAccessViewSet)
# questionnaires
router.register("records/questionnairetemplates", views.QuestionnaireTemplateViewSet)
router.register("records/questionnaires", views.QuestionnaireViewSet)
router.register("records/questionnaire_answers", views.QuestionnaireAnswersViewSet)
router.register("records/questionnaire_fields", views.QuestionnaireFieldsViewSet)
router.register("records/questionnaire_files", views.QuestionnaireFilesViewSet)
# records
router.register("records/recordtemplates", views.RecordTemplateViewSet)
router.register("records/records", views.RecordViewSet)
# encryptions
router.register("records/encryptions", views.RecordEncryptionNewViewSet)
# fields
router.register("records/recordstatefields", views.RecordStateFieldViewSet)
router.register("records/recordusersfields", views.RecordUsersFieldViewSet)
router.register("records/recordselectfields", views.RecordSelectFieldViewSet)
router.register("records/recordstandardfields", views.RecordStandardFieldViewSet)
router.register("records/recordmultiplefields", views.RecordMultipleFieldViewSet)
# fields encrypted
router.register(
    "records/recordencryptedselectfields", views.RecordEncryptedSelectFieldViewSet
)
router.register(
    "records/recordencryptedfilefields", views.RecordEncryptedFileFieldViewSet
)
router.register(
    "records/recordencryptedstandardfields", views.RecordEncryptedStandardFieldViewSet
)
# entries
router.register("records/recordstateentries", views.RecordStateEntryViewSet)
router.register("records/recordusersentries", views.RecordUsersEntryViewSet)
router.register("records/recordselectentries", views.RecordSelectEntryViewSet)
router.register("records/recordstandardentries", views.RecordStandardEntryViewSet)
router.register("records/recordmultipleentries", views.RecordMultipleEntryViewSet)
# entries encrypted
router.register(
    "records/recordencryptedselectentries", views.RecordEncryptedSelectEntryViewSet
)
router.register(
    "records/recordencryptedfileentries", views.RecordEncryptedFileEntryViewSet
)
router.register(
    "records/recordencryptedstandardentries", views.RecordEncryptedStandardEntryViewSet
)
# statistic
router.register("records/recordstatisticentries", views.RecordStatisticEntryViewSet)
