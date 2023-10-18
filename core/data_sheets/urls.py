from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()

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
]
