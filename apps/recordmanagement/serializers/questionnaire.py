from apps.recordmanagement.models import Questionnaire, RecordQuestionnaire, QuestionnaireField, QuestionnaireAnswer, \
    QuestionnaireFile
from rest_framework import serializers


###
# Other
###
class CodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class DataFileSerializer(serializers.Serializer):
    data = serializers.FileField()


class DataTextSerializer(serializers.Serializer):
    data = serializers.CharField()


###
# Questionnaire Field
###
class QuestionnaireFieldSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)  # used on forms populated from the property

    class Meta:
        model = QuestionnaireField
        fields = '__all__'


###
# QuestionnaireFile
###
class QuestionnaireFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireFile
        fields = '__all__'


###
# Questionnaire
###
class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['rlc'] = self.context['request'].user.rlc
        return attrs


class QuestionnaireFilesSerializer(QuestionnaireSerializer):
    files = QuestionnaireFileSerializer(many=True, read_only=True)


###
# QuestionnaireAnswer
###
class QuestionnaireAnswerSerializer(serializers.ModelSerializer):
    field = QuestionnaireFieldSerializer(read_only=True)

    class Meta:
        model = QuestionnaireAnswer
        exclude = ['aes_key']


class QuestionnaireAnswerRetrieveSerializer(QuestionnaireAnswerSerializer):
    data = serializers.CharField()


class QuestionnaireAnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireAnswer
        fields = '__all__'

    def get_instance(self):
        return QuestionnaireAnswer(**self.validated_data)


class QuestionnaireAnswerCreateFileSerializer(QuestionnaireAnswerCreateSerializer):
    data = serializers.FileField()

    def get_instance(self):
        instance = super().get_instance()
        instance.upload_file(self.validated_data['data'])
        return instance


class QuestionnaireAnswerCreateTextSerializer(QuestionnaireAnswerCreateSerializer):
    data = serializers.CharField()


###
# RecordQuestionnaire
###
class RecordQuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordQuestionnaire
        fields = '__all__'


class RecordQuestionnaireListSerializer(RecordQuestionnaireSerializer):
    questionnaire = QuestionnaireSerializer(read_only=True)
    # answers = QuestionnaireAnswerSerializer(many=True, read_only=True)


class RecordQuestionnaireDetailSerializer(RecordQuestionnaireSerializer):
    questionnaire = QuestionnaireFilesSerializer(read_only=True)
    fields = serializers.SerializerMethodField(method_name='get_questionnaire_fields')

    def get_questionnaire_fields(self, obj):
        fields = list(obj.questionnaire.fields.all())
        answers = list(obj.answers.values_list('field', flat=True))
        fields = list(filter(lambda field: field.id not in answers, fields))
        return QuestionnaireFieldSerializer(fields, many=True).data
