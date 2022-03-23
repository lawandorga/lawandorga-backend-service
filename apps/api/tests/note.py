from rest_framework.test import force_authenticate
from apps.api.tests.user import UserViewSetBase
from apps.api.static import PERMISSION_DASHBOARD_MANAGE_NOTES
from apps.api.models import Note
from apps.api.views import NoteViewSet
from django.test import TestCase


class NoteViewSetWorking(UserViewSetBase, TestCase):
    def setUp(self):
        super().setUp()
        self.rlc_user.grant(PERMISSION_DASHBOARD_MANAGE_NOTES)

    def create_note(self):
        self.note = Note.objects.create(rlc=self.rlc, title='Update 2022')

    def test_create_works(self):
        view = NoteViewSet.as_view(actions={'post': 'create'})
        data = {
            'title': 'My Note',
            'note': 'My awesome text within this note.'
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, 'My Note', status_code=201)

    def test_update_works(self):
        view = NoteViewSet.as_view(actions={'patch': 'partial_update'})
        self.create_note()
        data = {
            'title': 'New Title',
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.note.pk)
        self.assertContains(response, 'New Title', status_code=200)

    def test_destroy_works(self):
        self.create_note()
        pk = self.note.pk
        view = NoteViewSet.as_view(actions={'delete': 'destroy'})
        data = {
            'title': 'New Title',
        }
        request = self.factory.delete('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=pk)
        self.assertContains(response, '', status_code=204)

    def test_list_works(self):
        self.create_note()
        view = NoteViewSet.as_view(actions={'get': 'list'})
        request = self.factory.get('')
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, 'Update 2022', status_code=200)
