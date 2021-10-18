from apps.recordmanagement.serializers.questionnaire import QuestionnaireSerializer, RecordQuestionnaireSerializer, \
    RecordQuestionnaireDetailSerializer, CodeSerializer
from apps.recordmanagement.models import Questionnaire, RecordQuestionnaire
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.none()
    serializer_class = QuestionnaireSerializer

    def get_queryset(self):
        return Questionnaire.objects.filter(rlc=self.request.user.rlc)

    def perform_create(self, serializer):
        return serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[])
    def code(self, request, *args, **kwargs):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if RecordQuestionnaire.objects.filter(code=serializer.validated_data['code']).exists():
            return Response({'code': serializer.validated_data['code']}, status=status.HTTP_200_OK)
        return Response({'non_field_errors': 'There is no questionnaire with this code.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def publish(self, request, *args, **kwargs):
        serializer = RecordQuestionnaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(RecordQuestionnaireDetailSerializer(instance).data, status=status.HTTP_201_CREATED,
                        headers=headers)


class RecordQuestionnaireViewSet(mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = RecordQuestionnaire.objects.none()
    serializer_class = RecordQuestionnaireSerializer

    def get_queryset(self):
        return RecordQuestionnaire.objects.filter(questionnaire__rlc=self.request.user.rlc)
