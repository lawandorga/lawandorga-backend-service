import mimetypes

from django.http import FileResponse
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response

from core.questionnaires.models import Questionnaire, QuestionnaireAnswer
from core.questionnaires.views.serializers import (
    QuestionnaireAnswerRetrieveSerializer,
    QuestionnaireFileAnswerSerializer,
    QuestionnaireListSerializer,
    QuestionnaireSerializer,
    QuestionnaireTextAnswerSerializer,
    RecordQuestionnaireDetailSerializer,
)


###
# Questionnaire
###
class QuestionnaireViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
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

    def retrieve(self, request, *args, **kwargs):
        self.lookup_url_kwarg = "pk"
        self.lookup_field = "code"
        return super().retrieve(request, *args, **kwargs)

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

    def list(self, request, *args, **kwargs):
        questionnaires = self.get_queryset()
        data = QuestionnaireListSerializer(questionnaires, many=True).data
        # private_key_rlc = request.user.get_private_key_rlc(request=request)
        for index, questionnaire in enumerate(questionnaires):
            answers = questionnaire.answers.all()
            [answer.decrypt(request.user.rlc_user) for answer in answers]
            data[index]["answers"] = QuestionnaireAnswerRetrieveSerializer(
                answers, many=True
            ).data
        return Response(data)


###
# QuestionnaireAnswer
###
class QuestionnaireAnswersViewSet(viewsets.GenericViewSet):
    queryset = QuestionnaireAnswer.objects.none()

    def get_queryset(self):
        return QuestionnaireAnswer.objects.filter(
            questionnaire__template__rlc=self.request.user.rlc
        )

    @action(detail=True)
    def download_file(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.decrypt(request.user.rlc_user)
        if instance.data is None:
            raise NotFound("This file does not exist.")
        file = instance.download_file(instance.aes_key)
        response = FileResponse(
            file, content_type=mimetypes.guess_type(instance.data)[0]
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            instance.data.split("/")[-1]
        )
        return response
