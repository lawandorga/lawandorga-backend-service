from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

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
    path("records/v2/", include(api.records_router.urls)),
    path("", include(router.urls)),
    path("query/", include(api.query_router.urls)),
    path("deletions/", include(api.deletions_router.urls)),
    path("accesses/", include(api.accesses_router.urls)),
    path("templates/", include(api.templates_router.urls)),
    path("fields/", include(api.fields_router.urls)),
]
