from apps.recordmanagement.serializers.questionnaire import QuestionnaireSerializer, RecordQuestionnaireSerializer
from apps.recordmanagement.models import Questionnaire, RecordQuestionnaire
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.none()
    serializer_class = QuestionnaireSerializer

    def get_queryset(self):
        return Questionnaire.objects.filter(rlc=self.request.user.rlc)

    @action(detail=False, methods=['post'])
    def publish(self, request, *args, **kwargs):
        serializer = RecordQuestionnaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RecordQuestionnaireViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = RecordQuestionnaire.objects.none()
    serializer_class = RecordQuestionnaireSerializer

    def get_queryset(self):
        return RecordQuestionnaire.objects.filter(questionnaire__rlc=self.request.user.rlc)
