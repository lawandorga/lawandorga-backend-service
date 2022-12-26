from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from core.models import Org, RlcUser, UserProfile
from core.records.views import (
    RecordEncryptedFileEntryViewSet,
    RecordEncryptedFileFieldViewSet,
    RecordEncryptedSelectEntryViewSet,
    RecordEncryptedSelectFieldViewSet,
    RecordEncryptedStandardEntryViewSet,
    RecordEncryptedStandardFieldViewSet,
    RecordSelectEntryViewSet,
    RecordSelectFieldViewSet,
    RecordStandardEntryViewSet,
    RecordStandardFieldViewSet,
    RecordStateEntryViewSet,
    RecordStateFieldViewSet,
    RecordTemplateViewSet,
    RecordUsersEntryViewSet,
    RecordUsersFieldViewSet,
)


class RecordViewSetsPermissions(TestCase):
    views = [
        # template
        (
            RecordTemplateViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
            "list",
            "retrieve",
        ),
        # fields
        (
            RecordEncryptedStandardFieldViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
        ),
        (RecordStandardFieldViewSet, "create", "partial_update", "update", "destroy"),
        (
            RecordEncryptedFileFieldViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
        ),
        (RecordSelectFieldViewSet, "create", "partial_update", "update", "destroy"),
        (
            RecordEncryptedSelectFieldViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
        ),
        (RecordStateFieldViewSet, "create", "partial_update", "update", "destroy"),
        (RecordUsersFieldViewSet, "create", "partial_update", "update", "destroy"),
        # entry
        (
            RecordEncryptedSelectEntryViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
        ),
        (RecordSelectEntryViewSet, "create", "partial_update", "update", "destroy"),
        (
            RecordEncryptedFileEntryViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
        ),
        (RecordStandardEntryViewSet, "create", "partial_update", "update", "destroy"),
        (
            RecordEncryptedStandardEntryViewSet,
            "create",
            "partial_update",
            "update",
            "destroy",
        ),
        (RecordUsersEntryViewSet, "create", "partial_update", "update", "destroy"),
        (RecordStateEntryViewSet, "create", "partial_update", "update", "destroy"),
    ]

    action_mapper = {
        "create": "POST",
        "update": "PUT",
        "partial_update": "PATCH",
        "destroy": "DELETE",
        "list": "GET",
        "retrieve": "GET",
    }

    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email="dummy@rlcm.de", name="Dummy 1")
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser(
            user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )
        self.rlc_user.generate_keys(settings.DUMMY_USER_PASSWORD)
        self.rlc_user.save()

    def check_forbidden(self, view_class, actions):
        for action in actions:
            view = view_class.as_view(actions={self.action_mapper[action]: action})
            request = self.factory.generic(self.action_mapper[action], "")
            response = view(request)
            self.assertEqual(response.status_code, 401)

    def check_not_existent(self, view_class, actions):
        for action in actions:
            view = view_class.as_view(actions={self.action_mapper[action]: action})
            request = self.factory.generic(self.action_mapper[action], "")
            with self.assertRaises(AttributeError):
                view(request)

    def test_permissions(self):
        for view_class in self.views:
            self.check_forbidden(view_class[0], view_class[1:])
            non_existent = list(self.action_mapper.keys())
            [non_existent.remove(x) for x in view_class[1:]]
            self.check_not_existent(view_class[0], non_existent)
