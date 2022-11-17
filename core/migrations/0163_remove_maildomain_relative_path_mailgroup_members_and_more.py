# Generated by Django 4.1.3 on 2022-11-17 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0162_alter_mailaddress_unique_together_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="maildomain",
            name="relative_path",
        ),
        migrations.AddField(
            model_name="mailgroup",
            name="members",
            field=models.ManyToManyField(related_name="groups", to="core.mailuser"),
        ),
        migrations.AlterField(
            model_name="mailaddress",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="addresses",
                to="core.mailaccount",
            ),
        ),
        migrations.AlterField(
            model_name="mailaddress",
            name="domain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="addresses",
                to="core.maildomain",
            ),
        ),
    ]
