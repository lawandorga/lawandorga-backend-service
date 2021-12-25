from apps.recordmanagement.serializers.questionnaire import QuestionnaireQuestionSerializer
from apps.recordmanagement.models import QuestionnaireQuestion
from rest_framework import viewsets, mixins


class QuestionnaireFieldsViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet):
    queryset = QuestionnaireQuestion.objects.none()
    serializer_class = QuestionnaireQuestionSerializer

    def get_queryset(self):
        return QuestionnaireQuestion.objects.filter(questionnaire__rlc=self.request.user.rlc)
