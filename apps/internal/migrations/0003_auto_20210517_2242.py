# Generated by Django 3.1.6 on 2021-05-17 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal", "0002_auto_20210513_1349"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="date",
            field=models.DateField(),
        ),
    ]
