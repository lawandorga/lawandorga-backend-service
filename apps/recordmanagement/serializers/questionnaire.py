from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.recordmanagement.models import (Questionnaire, QuestionnaireAnswer,
                                          QuestionnaireQuestion,
                                          QuestionnaireTemplate,
                                          QuestionnaireTemplateFile)


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
# QuestionnaireQuestion
###
class QuestionnaireQuestionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        read_only=True
    )  # used on forms populated from the property

    class Meta:
        model = QuestionnaireQuestion
        fields = "__all__"


###
# QuestionnaireFile
###
class QuestionnaireTemplateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireTemplateFile
        fields = "__all__"


###
# QuestionnaireTemplate
###
class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireTemplate
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["rlc"] = self.context["request"].user.rlc
        return attrs


class QuestionnaireTemplateFilesSerializer(QuestionnaireTemplateSerializer):
    files = QuestionnaireTemplateFileSerializer(many=True, read_only=True)


###
# QuestionnaireAnswer
###
class QuestionnaireAnswerSerializer(serializers.ModelSerializer):
    field = QuestionnaireQuestionSerializer(read_only=True)

    class Meta:
        model = QuestionnaireAnswer
        exclude = ["aes_key"]


class QuestionnaireAnswerRetrieveSerializer(QuestionnaireAnswerSerializer):
    data = serializers.CharField()


class QuestionnaireAnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireAnswer
        fields = "__all__"

    def get_instance(self):
        return QuestionnaireAnswer(**self.validated_data)


class QuestionnaireFileAnswerSerializer(QuestionnaireAnswerCreateSerializer):
    data = serializers.FileField()

    def get_instance(self):
        instance = super().get_instance()
        instance.upload_file(self.validated_data["data"])
        return instance


class QuestionnaireTextAnswerSerializer(QuestionnaireAnswerCreateSerializer):
    data = serializers.CharField()

    def validate_data(self, data):
        if len(data) > 190:
            raise ValidationError(
                "The message can only be 190 characters long, because of encryption issues. "
                "Your message is {} characters long.".format(len(data))
            )
        return data


###
# RecordQuestionnaire
###
class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = "__all__"


class QuestionnaireListSerializer(QuestionnaireSerializer):
    template = QuestionnaireTemplateSerializer(read_only=True)
    # answers = QuestionnaireAnswerSerializer(many=True, read_only=True)


class RecordQuestionnaireDetailSerializer(QuestionnaireSerializer):
    template = QuestionnaireTemplateFilesSerializer(read_only=True)
    fields = serializers.SerializerMethodField(method_name="get_questionnaire_fields")

    def get_questionnaire_fields(self, obj):
        fields = list(obj.template.fields.all())
        answers = list(obj.answers.values_list("field", flat=True))
        fields = list(filter(lambda field: field.id not in answers, fields))
        return QuestionnaireQuestionSerializer(fields, many=True).data
