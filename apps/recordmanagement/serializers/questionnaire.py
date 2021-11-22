from apps.recordmanagement.models import Questionnaire, RecordQuestionnaire, QuestionnaireField, QuestionnaireAnswer
from rest_framework import serializers


class CodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['rlc'] = self.context['request'].user.rlc
        return attrs


class QuestionnaireFieldSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = QuestionnaireField
        fields = '__all__'


class QuestionnaireDetailSerializer(QuestionnaireSerializer):
    fields = QuestionnaireFieldSerializer(many=True, read_only=True)


class RecordQuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordQuestionnaire
        fields = '__all__'


class RecordQuestionnaireDetailSerializer(serializers.ModelSerializer):
    questionnaire = QuestionnaireDetailSerializer(read_only=True)
    fields = serializers.SerializerMethodField(method_name='get_questionnaire_fields')

    class Meta:
        model = RecordQuestionnaire
        fields = '__all__'

    def get_questionnaire_fields(self, obj):
        fields = list(obj.questionnaire.fields.all())
        answers = list(obj.answers.values_list('field', flat=True))
        fields = list(filter(lambda field: field.id not in answers, fields))
        return QuestionnaireFieldSerializer(fields, many=True).data


class RecordQuestionnaireUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordQuestionnaire
        fields = []


class QuestionnaireAnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireAnswer
        exclude = ['data']
