# Generated by Django 3.2.9 on 2021-12-25 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recordmanagement", "0096_rename_questionnaire_questionnaire_template"),
    ]

    operations = [
        migrations.RenameField(
            model_name="questionnaireanswer",
            old_name="record_questionnaire",
            new_name="questionnaire",
        ),
    ]
