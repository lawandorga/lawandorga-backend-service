# Generated by Django 3.0 on 2021-03-17 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("collab", "0006_auto_20210317_1517"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collabdocument",
            name="path",
            field=models.CharField(default="", max_length=4096),
        ),
    ]
