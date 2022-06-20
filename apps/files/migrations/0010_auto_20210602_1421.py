# Generated by Django 3.1.6 on 2021-06-02 12:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0063_auto_20210513_1441"),
        ("files", "0009_auto_20210601_1413"),
    ]

    operations = [
        migrations.AlterField(
            model_name="folder",
            name="rlc",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="folders",
                to="api.rlc",
            ),
        ),
    ]
