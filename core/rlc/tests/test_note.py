from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import Note, Org, Permission, RlcUser, UserProfile
from core.static import PERMISSION_DASHBOARD_MANAGE_NOTES, get_all_permission_strings
from core.views import NoteViewSet


class NoteUserBase:
    def setUp(self):
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1"
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True, org=self.rlc
        )
        self.rlc.generate_keys()
        self.rlc_user = RlcUser.objects.get(pk=self.rlc_user.pk)
        self.private_key = bytes(self.rlc_user.private_key).decode("utf-8")
        self.create_permissions()

    def create_permissions(self):
        for perm in get_all_permission_strings():
            Permission.objects.create(name=perm)


class NoteUserViewSetBase(NoteUserBase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()


class NoteViewSetWorking(NoteUserViewSetBase, TestCase):
    def setUp(self):
        super().setUp()
        self.rlc_user.grant(PERMISSION_DASHBOARD_MANAGE_NOTES)

    def create_note(self):
        self.note = Note.objects.create(rlc=self.rlc, title="Update 2022")

    def test_create_works(self):
        view = NoteViewSet.as_view(actions={"post": "create"})
        data = {"title": "My Note", "note": "My awesome text within this note."}
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "My Note", status_code=201)

    def test_update_works(self):
        view = NoteViewSet.as_view(actions={"patch": "partial_update"})
        self.create_note()
        data = {
            "title": "New Title",
        }
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.note.pk)
        self.assertContains(response, "New Title", status_code=200)

    def test_destroy_works(self):
        self.create_note()
        pk = self.note.pk
        view = NoteViewSet.as_view(actions={"delete": "destroy"})
        data = {
            "title": "New Title",
        }
        request = self.factory.delete("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=pk)
        self.assertContains(response, "", status_code=204)

    def test_list_works(self):
        self.create_note()
        view = NoteViewSet.as_view(actions={"get": "list"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "Update 2022", status_code=200)