# Generated by Django 4.1.2 on 2022-10-27 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0142_merge_0141_create_fixtures_0141_merge_20221024_1325"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="legalrequirementuser",
            unique_together={("legal_requirement", "rlc_user")},
        ),
    ]