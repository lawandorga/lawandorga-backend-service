from apps.recordmanagement.serializers.questionnaire import QuestionnaireFieldSerializer
from apps.recordmanagement.models import QuestionnaireField
from rest_framework import viewsets, mixins


class QuestionnaireFieldsViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet):
    queryset = QuestionnaireField.objects.none()
    serializer_class = QuestionnaireFieldSerializer

    def get_queryset(self):
        return QuestionnaireField.objects.filter(questionnaire__rlc=self.request.user.rlc)
