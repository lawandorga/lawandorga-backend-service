from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.api.fixtures import create_permissions
from apps.api.models import (HasPermission, Permission, Rlc, RlcUser,
                             UserProfile)
from apps.api.static import (PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES,
                             PERMISSION_RECORDS_ADD_RECORD)
from apps.recordmanagement.models import (Record, RecordEncryptionNew,
                                          RecordTemplate)
from apps.recordmanagement.views import RecordTemplateViewSet, RecordViewSet


###
# General
###
class BaseRecord:
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1", rlc=self.rlc
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )
        self.template = RecordTemplate.objects.create(
            rlc=self.rlc, name="Record Template"
        )
        # permissions
        create_permissions()
        permission = Permission.objects.get(name=PERMISSION_RECORDS_ADD_RECORD)
        HasPermission.objects.create(
            user_has_permission=self.user, permission=permission
        )
        permission = Permission.objects.get(
            name=PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES
        )
        HasPermission.objects.create(
            user_has_permission=self.user, permission=permission
        )
        # HasPermission.objects.create(user_has_permission=self.user, permission=)

    def create_user(self, email, name):
        user = UserProfile.objects.create(email=email, name=name, rlc=self.rlc)
        user.set_password("pass1234")
        user.save()
        RlcUser.objects.create(
            user=user, accepted=True, locked=False, email_confirmed=True, is_active=True
        )


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
# Fields
###
pass


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
        self.record = Record.objects.create(template=self.template)

    def test_record_create(self):
        view = RecordViewSet.as_view(actions={"post": "create"})
        data = {
            "template": self.template.pk,
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Record.objects.filter(template=self.template.pk).count(), 1)
        self.assertTrue(RecordEncryptionNew.objects.count(), 1)

    def test_record_delete(self):
        self.setup_record()
        view = RecordViewSet.as_view(actions={"delete": "destroy"})
        request = self.factory.delete("")
        force_authenticate(request, self.user)
        response = view(request, pk=self.record.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Record.objects.filter(pk=self.record.pk).count(), 0)


###
# Entries
###
pass
