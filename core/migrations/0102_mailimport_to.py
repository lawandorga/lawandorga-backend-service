# Generated by Django 5.0.2 on 2024-04-02 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0101_remove_mailimport_content_remove_mailimport_subject_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailimport",
            name="to",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]