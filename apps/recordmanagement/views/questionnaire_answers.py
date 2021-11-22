from apps.recordmanagement.models import QuestionnaireAnswer
from rest_framework.decorators import action
from rest_framework import viewsets
from django.http import FileResponse
import mimetypes


class QuestionnaireAnswersViewSet(viewsets.GenericViewSet):
    queryset = QuestionnaireAnswer.objects.none()

    def get_queryset(self):
        return QuestionnaireAnswer.objects.filter(record_questionnaire__questionnaire__rlc=self.request.user.rlc)

    @action(detail=True)
    def download_file(self, request, *args, **kwargs):
        instance = self.get_object()
        file, delete = instance.download_file()
        response = FileResponse(file, content_type=mimetypes.guess_type(instance.data)[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.data.split('/')[-1])
        delete()
        return response
