from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import HasPermission, Org, Permission, RlcUser, UserProfile
from core.records.models import RecordTemplate
from core.records.views import RecordTemplateViewSet
from core.seedwork import test_helpers
from core.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES,
    PERMISSION_RECORDS_ADD_RECORD,
)


###
# General
###
class BaseRecord:
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1"
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser(
            user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )
        self.rlc_user.generate_keys(settings.DUMMY_USER_PASSWORD)
        self.rlc_user.save()
        self.template = RecordTemplate.objects.create(
            rlc=self.rlc, name="Record Template"
        )
        # permissions
        permission = Permission.objects.get(name=PERMISSION_RECORDS_ADD_RECORD)
        HasPermission.objects.create(user=self.user.rlc_user, permission=permission)
        permission = Permission.objects.get(
            name=PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES
        )
        HasPermission.objects.create(user=self.rlc_user, permission=permission)
        # HasPermission.objects.create(user_has_permission=self.user, permission=)

    def create_user(self, email, name):
        user = UserProfile.objects.create(email=email, name=name)
        user.set_password(settings.DUMMY_USER_PASSWORD)
        user.save()
        r = RlcUser(
            user=user,
            accepted=True,
            locked=False,
            email_confirmed=True,
            is_active=True,
            org=self.rlc,
        )
        r.generate_keys(settings.DUMMY_USER_PASSWORD)
        r.save()


###
# Template
###
class RecordTemplateViewSetWorking(BaseRecord, TestCase):
    def setup_record_template(self):
        self.record_template = RecordTemplate.objects.create(
            name="RecordTemplate 121", rlc=self.rlc
        )

    def test_record_template_create(self):
        view = RecordTemplateViewSet.as_view(actions={"post": "create"})
        data = {
            "name": "RecordTemplate 121",
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(
            RecordTemplate.objects.filter(pk=response.data["id"]).count(), 0
        )

    def test_record_template_delete(self):
        self.setup_record_template()
        view = RecordTemplateViewSet.as_view(actions={"delete": "destroy"})
        request = self.factory.delete("")
        force_authenticate(request, self.user)
        pk = self.record_template.pk
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordTemplate.objects.filter(pk=pk).count(), 0)

    def test_record_template_update(self):
        self.setup_record_template()
        view = RecordTemplateViewSet.as_view(actions={"patch": "partial_update"})
        data = {"name": "RecordTemplate 145"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.record_template.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            RecordTemplate.objects.filter(name="RecordTemplate 145").count(), 1
        )


###
# Record
###
class RecordViewSetWorking(BaseRecord, TestCase):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(
            rlc=self.rlc, name="Record Template"
        )

    def setup_record(self):
        self.record = test_helpers.create_record(
            template=self.template, users=[self.user]
        )["record"]
        self.record.put_in_folder(self.rlc_user)
