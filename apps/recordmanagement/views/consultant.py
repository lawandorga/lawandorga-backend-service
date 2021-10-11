from rest_framework.viewsets import GenericViewSet
from apps.api.serializers import UserProfileNameSerializer
from apps.api.models import UserProfile
from rest_framework import mixins


class ConsultantViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = UserProfile.objects.none()
    serializer_class = UserProfileNameSerializer

    def get_queryset(self):
        return self.request.user.rlc.get_consultants()
