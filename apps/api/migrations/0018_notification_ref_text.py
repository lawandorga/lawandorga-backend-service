# Generated by Django 2.2.8 on 2020-07-15 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_notification_read"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="ref_text",
            field=models.CharField(max_length=100, null=True),
        ),
    ]