from apps.recordmanagement.serializers.record import RecordTemplateSerializer, RecordTextFieldSerializer, \
    RecordFieldSerializer
from apps.recordmanagement.models.record import RecordTemplate, RecordField
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets


###
# Template
###
class RecordTemplateViewSet(viewsets.ModelViewSet):
    queryset = RecordTemplate.objects.none()
    serializer_class = RecordTemplateSerializer

    def get_queryset(self):
        return RecordTemplate.objects.filter(rlc=self.request.user.rlc)

    @action(detail=True, methods=['get'])
    def fields(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.fields.all()
        serializer = RecordFieldSerializer(queryset, many=True)
        return Response(serializer.data)


###
# Fields
###
class RecordTextFieldViewSet(viewsets.ModelViewSet):
    queryset = RecordField.objects.none()
    serializer_class = RecordTextFieldSerializer

    def get_queryset(self):
        return RecordField.objects.filter(template__rlc=self.request.user.rlc)
