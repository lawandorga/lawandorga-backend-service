# Generated by Django 3.1.6 on 2021-06-01 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0006_auto_20210324_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='key',
            field=models.SlugField(allow_unicode=True, null=True),
        ),
    ]
