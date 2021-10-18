from apps.recordmanagement.models import Questionnaire, RecordQuestionnaire
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


class RecordQuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordQuestionnaire
        fields = '__all__'


class RecordQuestionnaireDetailSerializer(serializers.ModelSerializer):
    questionnaire = QuestionnaireSerializer(read_only=True)

    class Meta:
        model = RecordQuestionnaire
        fields = '__all__'
