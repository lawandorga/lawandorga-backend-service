# Generated by Django 3.1.6 on 2021-06-04 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0011_auto_20210602_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='exists',
            field=models.BooleanField(default=True),
        ),
    ]
