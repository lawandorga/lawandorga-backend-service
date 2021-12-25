from apps.recordmanagement.serializers.questionnaire import QuestionnaireTemplateSerializer, QuestionnaireSerializer, \
    RecordQuestionnaireDetailSerializer, CodeSerializer, \
    QuestionnaireQuestionSerializer, QuestionnaireFileAnswerSerializer, QuestionnaireTextAnswerSerializer, \
    QuestionnaireTemplateFileSerializer, QuestionnaireListSerializer, QuestionnaireAnswerRetrieveSerializer
from apps.recordmanagement.models import QuestionnaireTemplate, Questionnaire
from rest_framework.exceptions import ParseError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplate.objects.none()
    serializer_class = QuestionnaireTemplateSerializer

    def get_queryset(self):
        return QuestionnaireTemplate.objects.filter(rlc=self.request.user.rlc)

    def perform_create(self, serializer):
        return serializer.save()

    @action(detail=True, methods=['get'])
    def fields(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.fields.all()
        serializer = QuestionnaireQuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def files(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.files.all()
        serializer = QuestionnaireTemplateFileSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[])
    def code(self, request, *args, **kwargs):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Questionnaire.objects.filter(code=serializer.validated_data['code']).exists():
            return Response({'code': serializer.validated_data['code']}, status=status.HTTP_200_OK)
        return Response({'non_field_errors': 'There is no questionnaire with this code.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def publish(self, request, *args, **kwargs):
        serializer = QuestionnaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(RecordQuestionnaireDetailSerializer(instance).data, status=status.HTTP_201_CREATED,
                        headers=headers)


class QuestionnaireViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Questionnaire.objects.none()
    serializer_class = QuestionnaireSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'partial_update']:
            return []
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ['retrieve', 'partial_update']:
            return Questionnaire.objects.all()
        if self.action in ['list']:
            record = self.request.query_params.get('record')
            if record is not None:
                return Questionnaire.objects.filter(record__template__rlc=self.request.user.rlc, record_id=record)
        return Questionnaire.objects.filter(template__rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'partial_update']:
            return RecordQuestionnaireDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        self.lookup_url_kwarg = 'pk'
        self.lookup_field = 'code'
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # save the fields
        for field in list(instance.template.fields.all()):
            if field.name in request.data and request.data[field.name]:
                data = {'questionnaire': instance.pk, 'field': field.pk, 'data': request.data[field.name]}
                if field.type == 'FILE':
                    answer_serializer = QuestionnaireFileAnswerSerializer(data=data)
                else:
                    answer_serializer = QuestionnaireTextAnswerSerializer(data=data)
                if answer_serializer.is_valid(raise_exception=False):
                    answer = answer_serializer.get_instance()
                    answer.encrypt()
                    answer.save()
                else:
                    print(answer_serializer.errors)
                    raise ParseError({field.name: answer_serializer.errors['data']})
        # return
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        questionnaires = self.get_queryset()
        data = QuestionnaireListSerializer(questionnaires, many=True).data
        private_key_rlc = request.user.get_private_key_rlc(request=request)
        for index, questionnaire in enumerate(questionnaires):
            answers = questionnaire.answers.all()
            [answer.decrypt(private_key_rlc) for answer in answers]
            data[index]['answers'] = QuestionnaireAnswerRetrieveSerializer(answers, many=True).data
        return Response(data)
