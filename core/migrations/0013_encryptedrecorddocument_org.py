# Generated by Django 4.1.4 on 2022-12-20 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_encryptedrecorddocument_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="encryptedrecorddocument",
            name="org",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="files",
                to="core.org",
            ),
        ),
    ]
