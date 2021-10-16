from apps.recordmanagement.serializers.questionnaire import QuestionnaireSerializer
from apps.recordmanagement.models import Questionnaire
from rest_framework import viewsets


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.none()
    serializer_class = QuestionnaireSerializer

    def get_queryset(self):
        return Questionnaire.objects.filter(rlc=self.request.user.rlc)
