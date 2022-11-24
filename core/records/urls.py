from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..seedwork.repository import RepositoryWarehouse
from . import api, views
from .models.upgrade import DjangoRecordUpgradeRepository

RepositoryWarehouse.add_repository(DjangoRecordUpgradeRepository)

router = DefaultRouter()

router.register("messages", views.MessageViewSet)
router.register("pool_records", views.PoolRecordViewSet)
router.register("pool_consultants", views.PoolConsultantViewSet)
router.register("record_documents", views.EncryptedRecordDocumentViewSet)
# record access and deletion
router.register("deletions", views.RecordDeletionViewSet)
router.register("accesses", views.RecordAccessViewSet)
# questionnaires
router.register("questionnairetemplates", views.QuestionnaireTemplateViewSet)
router.register("questionnaires", views.QuestionnaireViewSet)
router.register("questionnaire_answers", views.QuestionnaireAnswersViewSet)
router.register("questionnaire_fields", views.QuestionnaireFieldsViewSet)
router.register("questionnaire_files", views.QuestionnaireFilesViewSet)
# records
router.register("recordtemplates", views.RecordTemplateViewSet)
router.register("records", views.RecordViewSet)
# encryptions
router.register("encryptions", views.RecordEncryptionNewViewSet)
# fields
router.register("recordstatefields", views.RecordStateFieldViewSet)
router.register("recordusersfields", views.RecordUsersFieldViewSet)
router.register("recordselectfields", views.RecordSelectFieldViewSet)
router.register("recordstandardfields", views.RecordStandardFieldViewSet)
router.register("recordmultiplefields", views.RecordMultipleFieldViewSet)
# fields encrypted
router.register("recordencryptedselectfields", views.RecordEncryptedSelectFieldViewSet)
router.register("recordencryptedfilefields", views.RecordEncryptedFileFieldViewSet)
router.register(
    "recordencryptedstandardfields", views.RecordEncryptedStandardFieldViewSet
)
# entries
router.register("recordstateentries", views.RecordStateEntryViewSet)
router.register("recordusersentries", views.RecordUsersEntryViewSet)
router.register("recordselectentries", views.RecordSelectEntryViewSet)
router.register("recordstandardentries", views.RecordStandardEntryViewSet)
router.register("recordmultipleentries", views.RecordMultipleEntryViewSet)
# entries encrypted
router.register("recordencryptedselectentries", views.RecordEncryptedSelectEntryViewSet)
router.register("recordencryptedfileentries", views.RecordEncryptedFileEntryViewSet)
router.register(
    "recordencryptedstandardentries", views.RecordEncryptedStandardEntryViewSet
)
# statistic
router.register("recordstatisticentries", views.RecordStatisticEntryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("records/", include(api.records_router.urls)),
    path("query/", include(api.query_router.urls)),
    path("questionnaires/v2/", include(api.questionnaire_router.urls)),
]
