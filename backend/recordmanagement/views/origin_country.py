from backend.recordmanagement.models.origin_country import OriginCountry
from backend.recordmanagement import serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins


class OriginCountryViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = OriginCountry.objects.all()
    serializer_class = serializers.OriginCountrySerializer
