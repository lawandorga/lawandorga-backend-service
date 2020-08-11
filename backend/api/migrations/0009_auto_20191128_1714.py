# Generated by Django 2.2.2 on 2019-11-28 16:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_auto_20190411_1633"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newuserrequest",
            name="request_processed",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="new_user_requests_processed",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
