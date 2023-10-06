import mimetypes

from django.db.models import ProtectedError
from django.http import FileResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response

from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES
from core.questionnaires.models import (
    Questionnaire,
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireTemplate,
    QuestionnaireTemplateFile,
)
from core.questionnaires.views.serializers import (
    CodeSerializer,
    QuestionnaireAnswerRetrieveSerializer,
    QuestionnaireFileAnswerSerializer,
    QuestionnaireListSerializer,
    QuestionnaireQuestionSerializer,
    QuestionnaireSerializer,
    QuestionnaireTemplateFileSerializer,
    QuestionnaireTemplateSerializer,
    QuestionnaireTextAnswerSerializer,
    RecordQuestionnaireDetailSerializer,
)
from core.seedwork.permission import CheckPermissionWall


###
# QuestionnaireTemplate
###
class QuestionnaireTemplateViewSet(
    CheckPermissionWall,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = QuestionnaireTemplate.objects.none()
    serializer_class = QuestionnaireTemplateSerializer
    permission_wall = {
        "partial_update": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
        "update": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
        "destroy": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
    }

    def get_queryset(self):
        return QuestionnaireTemplate.objects.filter(rlc=self.request.user.rlc)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ParseError(
                "This questionnaire template can not be deleted, because there are questionnaires "
                "within records that use it."
            )

    @action(detail=True, methods=["get"])
    def fields(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.fields.all()
        serializer = QuestionnaireQuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def files(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.files.all()
        serializer = QuestionnaireTemplateFileSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[])
    def code(self, request, *args, **kwargs):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Questionnaire.objects.filter(
            code=serializer.validated_data["code"]
        ).exists():
            return Response(
                {"code": serializer.validated_data["code"]}, status=status.HTTP_200_OK
            )
        return Response(
            {"non_field_errors": "There is no questionnaire with this code."},
            status=status.HTTP_400_BAD_REQUEST,
        )


###
# QuestionnaireFile
###
class QuestionnaireFilesViewSet(
    CheckPermissionWall,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = QuestionnaireTemplateFile.objects.none()
    serializer_class = QuestionnaireTemplateFileSerializer
    permission_wall = {
        "create": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
        "destroy": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
    }

    def get_permissions(self):
        if self.action in ["retrieve"]:
            return []
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ["retrieve"]:
            return QuestionnaireTemplateFile.objects.all()
        return QuestionnaireTemplateFile.objects.filter(
            questionnaire__rlc=self.request.user.rlc
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        response = FileResponse(
            instance.file, content_type=mimetypes.guess_type(instance.file.name)[0]
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            instance.name
        )
        return response


###
# QuestionnaireField
###
class QuestionnaireFieldsViewSet(
    CheckPermissionWall,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = QuestionnaireQuestion.objects.none()
    serializer_class = QuestionnaireQuestionSerializer
    permission_wall = {
        "create": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
        "partial_update": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
        "update": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
        "destroy": PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES,
    }

    def get_queryset(self):
        return QuestionnaireQuestion.objects.filter(
            questionnaire__rlc=self.request.user.rlc
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
