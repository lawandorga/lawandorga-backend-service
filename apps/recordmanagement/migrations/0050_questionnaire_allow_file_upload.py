# Generated by Django 3.1.6 on 2021-10-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0049_recordquestionnaire_answered'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='allow_file_upload',
            field=models.BooleanField(default=True),
        ),
    ]
