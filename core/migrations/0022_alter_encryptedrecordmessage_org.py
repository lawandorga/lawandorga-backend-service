# Generated by Django 4.1.4 on 2022-12-30 22:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_alter_encryptedrecordmessage_record"),
    ]

    operations = [
        migrations.AlterField(
            model_name="encryptedrecordmessage",
            name="org",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="core.org",
            ),
            preserve_default=False,
        ),
    ]
