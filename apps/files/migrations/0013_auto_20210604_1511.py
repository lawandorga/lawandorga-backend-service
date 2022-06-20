# Generated by Django 3.1.6 on 2021-06-04 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0012_file_exists"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="key",
            field=models.SlugField(
                allow_unicode=True, max_length=1000, null=True, unique=True
            ),
        ),
    ]
