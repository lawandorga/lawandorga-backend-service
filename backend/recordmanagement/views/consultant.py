from rest_framework.viewsets import GenericViewSet
from backend.api.serializers import UserProfileForeignSerializer
from backend.api.models import UserProfile
from rest_framework import mixins


class ConsultantViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = UserProfile.objects.none()
    serializer_class = UserProfileForeignSerializer

    def get_queryset(self):
        return self.request.user.rlc.get_consultants()
