from apps.recordmanagement.serializers.questionnaire import QuestionnaireTemplateFileSerializer
from apps.recordmanagement.models import QuestionnaireTemplateFile
from rest_framework import viewsets, mixins
from django.http import FileResponse
import mimetypes


class QuestionnaireFilesViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = QuestionnaireTemplateFile.objects.none()
    serializer_class = QuestionnaireTemplateFileSerializer

    def get_permissions(self):
        if self.action in ['retrieve']:
            return []
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ['retrieve']:
            return QuestionnaireTemplateFile.objects.all()
        return QuestionnaireTemplateFile.objects.filter(questionnaire__rlc=self.request.user.rlc)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        response = FileResponse(instance.file, content_type=mimetypes.guess_type(instance.file.name)[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        return response
