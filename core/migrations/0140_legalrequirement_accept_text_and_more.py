# Generated by Django 4.1.2 on 2022-10-20 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0139_merge_20221019_1705"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalrequirement",
            name="accept_text",
            field=models.CharField(default="Accepted", max_length=1000),
        ),
        migrations.AddField(
            model_name="legalrequirement",
            name="button_text",
            field=models.CharField(default="Accept", max_length=1000),
        ),
    ]