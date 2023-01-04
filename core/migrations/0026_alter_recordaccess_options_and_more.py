# Generated by Django 4.1.4 on 2023-01-04 20:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0025_alter_mailaddress_options_recordaccess_processor_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recordaccess",
            options={
                "ordering": ["-created"],
                "verbose_name": "RecordAccess",
                "verbose_name_plural": "RecordAccesses",
            },
        ),
        migrations.AlterField(
            model_name="recordaccess",
            name="requested_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="requestedrecordaccesses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
