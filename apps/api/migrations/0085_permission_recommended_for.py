# Generated by Django 3.2.11 on 2022-02-10 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0084_permission_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="permission",
            name="recommended_for",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
    ]
