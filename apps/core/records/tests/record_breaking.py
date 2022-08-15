import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import force_authenticate

from apps.recordmanagement.models import (
    Record,
    RecordEncryptedSelectEntry,
    RecordEncryptedSelectField,
    RecordEncryptedStandardEntry,
    RecordEncryptedStandardField,
    RecordMultipleEntry,
    RecordMultipleField,
    RecordSelectEntry,
    RecordSelectField,
    RecordStandardField,
    RecordStateEntry,
    RecordStateField,
)
from .record import BaseRecord
from apps.core.records.tests.record_entries import BaseRecordEntry
from apps.recordmanagement.views import (
    RecordEncryptedSelectEntryViewSet,
    RecordEncryptedStandardEntryViewSet,
    RecordMultipleEntryViewSet,
    RecordSelectEntryViewSet,
    RecordStandardEntryViewSet,
    RecordStateEntryViewSet,
    RecordStateFieldViewSet,
)


###
# Fields
###
class RecordStateFieldViewSetErrors(BaseRecord, TestCase):
    def setup_field(self):
        self.field = RecordStateField.objects.create(
            template=self.template, options=["Closed", "Option 2"]
        )

    def test_field_can_not_be_created_without_closed(self):
        view = RecordStateFieldViewSet.as_view(actions={"post": "create"})
        data = {
            "name": "Field",
            "template": self.template.pk,
            "options": json.dumps(["Option 1", "Option 2", "Open"]),
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "options", status_code=400)

    def test_field_can_not_be_updated_without_closed(self):
        self.setup_field()
        view = RecordStateFieldViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "name": "Field",
            "template": self.template.pk,
            "options": json.dumps(["Option 1", "Option 2", "Open"]),
        }
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.field.pk)
        self.assertContains(response, "options", status_code=400)

    def test_field_can_not_be_created_without_open(self):
        view = RecordStateFieldViewSet.as_view(actions={"post": "create"})
        data = {
            "name": "Field",
            "template": self.template.pk,
            "options": json.dumps(["Option 1", "Option 2", "Closed"]),
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "options", status_code=400)

    def test_field_can_not_be_updated_without_open(self):
        self.setup_field()
        view = RecordStateFieldViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "name": "Field",
            "template": self.template.pk,
            "options": json.dumps(["Option 1", "Option 2", "Closed"]),
        }
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.field.pk)
        self.assertContains(response, "options", status_code=400)


###
# Entries
###
class RecordStateEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        RecordStateField.objects.all().delete()
        self.field = RecordStateField.objects.create(
            template=self.template, options=["Closed", "Option 1"]
        )

    def setup_entry(self):
        self.entry = RecordStateEntry.objects.create(
            record=self.record, field=self.field, value="Option 1"
        )

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordStateEntryViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "value": json.dumps(["Option 3"]),
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertContains(response, "state", status_code=400)

    def test_no_500_on_create_with_value_missing(self):
        view = RecordStateEntryViewSet.as_view(actions={"post": "create"})
        data = {
            "record": self.record.pk,
            "field": self.field.pk,
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_no_500_on_update_with_value_missing(self):
        self.setup_entry()
        view = RecordStateEntryViewSet.as_view(actions={"patch": "partial_update"})
        data = {}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)


class RecordStandardEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordStandardField.objects.create(template=self.template)

    def test_no_500_on_create_with_value_missing(self):
        view = RecordStandardEntryViewSet.as_view(actions={"post": "create"})
        data = {
            "record": self.record.pk,
            "field": self.field.pk,
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 400)


class RecordEncryptedStandardEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedStandardField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordEncryptedStandardEntry(
            record=self.record, field=self.field, value="Test Text"
        )
        self.entry.encrypt(aes_key_record=self.aes_key_record)
        self.entry.save()
        self.entry.decrypt(aes_key_record=self.aes_key_record)

    def test_weird_values_work_on_update(self):
        self.setup_entry()
        view = RecordEncryptedStandardEntryViewSet.as_view(
            actions={"patch": "partial_update"}
        )
        data = {
            "url": "whatever should be ignored",
            "value": json.dumps({"isTrusted": True}),
        }
        request = self.factory.patch("", data=data, format="json")
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        entry = RecordEncryptedStandardEntry.objects.first()
        entry.decrypt(aes_key_record=self.aes_key_record)
        self.assertEqual(entry.value, json.dumps({"isTrusted": True}))

    def test_no_500_on_create_with_value_missing(self):
        view = RecordEncryptedStandardEntryViewSet.as_view(actions={"post": "create"})
        data = {
            "record": self.record.pk,
            "field": self.field.pk,
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_no_500_on_update_with_value_missing(self):
        self.setup_entry()
        view = RecordEncryptedStandardEntryViewSet.as_view(
            actions={"patch": "partial_update"}
        )
        data = {}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)


class RecordSelectEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordSelectField.objects.create(
            template=self.template, options=["Option 2", "Option 1"]
        )

    def setup_entry(self):
        self.entry = RecordSelectEntry.objects.create(
            record=self.record, field=self.field, value=["Option 1"]
        )

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "value": "Option 3",
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertContains(response, "value", status_code=400)

    def test_only_one_value_can_be_selected(self):
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "value": json.dumps(["Option 1", "Option 2"]),
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 400)


class RecordMultipleEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordMultipleField.objects.create(
            template=self.template, options=["Option 2", "Option 1"]
        )

    def setup_entry(self):
        self.entry = RecordMultipleEntry.objects.create(
            record=self.record, field=self.field, value=["Option 1"]
        )

    def test_multiple_values_can_be_selected(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordMultipleEntryViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "value": json.dumps(["Option 1", "Option 2"]),
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)

    def test_values_must_be_in_options(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordMultipleEntryViewSet.as_view(actions={"patch": "partial_update"})
        data = {
            "value": json.dumps(["Option 2", "Option 3"]),
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 400)


class RecordEncryptedSelectEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedSelectField.objects.create(
            template=self.template, options=["Option 1", "Option 2"]
        )

    def setup_entry(self):
        entry = RecordEncryptedSelectEntry(
            record=self.record, field=self.field, value=json.dumps(["Option 1"])
        )
        entry.encrypt(aes_key_record=self.aes_key_record)
        entry.save()
        self.entry = RecordEncryptedSelectEntry.objects.first()

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(
            actions={"patch": "partial_update"}
        )
        data = {
            "value": "Option 3",
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 400)

    def test_only_one_value_can_be_selected(self):
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(
            actions={"patch": "partial_update"}
        )
        data = {
            "value": json.dumps(["Option 1", "Option 2"]),
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 400)


class RecordTimeUpdateOnEntryUpdateOrCreate(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedStandardField.objects.create(
            template=self.template, name="Test"
        )

    def setup_entry(self):
        entry = RecordEncryptedStandardEntry(
            record=self.record, field=self.field, value="Test"
        )
        entry.encrypt(aes_key_record=self.aes_key_record)
        entry.save()
        self.entry = RecordEncryptedStandardEntry.objects.first()

    def test_time_updated_on_create(self):
        self.record.updated = timezone.now() - timedelta(days=2)
        self.record.save()
        view = RecordEncryptedStandardEntryViewSet.as_view(actions={"post": "create"})
        data = {
            "record": self.record.pk,
            "field": self.field.pk,
            "value": "Hallo",
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        view(request)
        record = Record.objects.get(pk=self.record.pk)
        self.assertGreater(record.updated, timezone.now() - timedelta(days=1))

    def test_time_updated_on_update(self):
        self.record.updated = timezone.now() - timedelta(days=2)
        self.record.save()
        self.setup_entry()
        view = RecordEncryptedStandardEntryViewSet.as_view(
            actions={"patch": "partial_update"}
        )
        data = {
            "value": "Test",
        }
        request = self.factory.patch("", data=data)
        force_authenticate(request, self.user)
        view(request, pk=self.entry.pk)
        record = Record.objects.get(pk=self.record.pk)
        self.assertGreater(record.updated, timezone.now() - timedelta(days=1))
