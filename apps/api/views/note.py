from rest_framework.viewsets import GenericViewSet
from apps.api.serializers import NoteSerializer
from apps.api.static import PERMISSION_ADMIN_MANAGE_NOTES
from apps.api.models import Note
from rest_framework import mixins


class NoteViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                  GenericViewSet):
    serializer_class = NoteSerializer
    permission_wall = {
        'create': PERMISSION_ADMIN_MANAGE_NOTES,
        'update': PERMISSION_ADMIN_MANAGE_NOTES,
        'partial_update': PERMISSION_ADMIN_MANAGE_NOTES,
        'destroy': PERMISSION_ADMIN_MANAGE_NOTES,
    }
    queryset = Note.objects.none()

    def get_queryset(self):
        return Note.objects.filter(rlc=self.request.user.rlc)
