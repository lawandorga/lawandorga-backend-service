from rest_framework import mixins, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from core.questionnaires.models import Questionnaire
from core.questionnaires.views.serializers import (
    QuestionnaireFileAnswerSerializer,
    QuestionnaireSerializer,
    QuestionnaireTextAnswerSerializer,
    RecordQuestionnaireDetailSerializer,
)


###
# Questionnaire
###
class QuestionnaireViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Questionnaire.objects.none()
    serializer_class = QuestionnaireSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "partial_update"]:
            return []
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ["retrieve", "partial_update"]:
            return Questionnaire.objects.all()
        if self.action in ["list"]:
            record = self.request.query_params.get("record")
            if record is not None:
                return Questionnaire.objects.filter(
                    record__template__rlc=self.request.user.rlc, record_id=record
                )
        return Questionnaire.objects.filter(template__rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ["retrieve", "partial_update"]:
            return RecordQuestionnaireDetailSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # save the fields
        for field in list(instance.template.fields.all()):
            if field.name in request.data and request.data[field.name]:
                data = {
                    "questionnaire": instance.pk,
                    "field": field.pk,
                    "data": request.data[field.name],
                }
                if field.type == "FILE":
                    answer_serializer = QuestionnaireFileAnswerSerializer(data=data)
                else:
                    answer_serializer = QuestionnaireTextAnswerSerializer(data=data)
                if answer_serializer.is_valid(raise_exception=False):
                    answer = answer_serializer.get_instance()
                    answer.encrypt()
                    answer.save()
                else:
                    raise ParseError({field.name: answer_serializer.errors["data"]})
        # return
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
