# Generated by Django 3.2.9 on 2021-12-25 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recordmanagement", "0091_rename_recordquestionnaire_questionnaire"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="QuestionnaireField",
            new_name="QuestionnaireQuestion",
        ),
    ]
