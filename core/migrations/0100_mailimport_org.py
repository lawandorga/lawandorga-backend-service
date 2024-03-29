# Generated by Django 5.0.2 on 2024-03-28 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0099_mailimport_cc"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailimport",
            name="org",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mail_imports",
                to="core.org",
            ),
            preserve_default=False,
        ),
    ]
