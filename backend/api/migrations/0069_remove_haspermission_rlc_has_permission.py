# Generated by Django 3.1.6 on 2021-07-27 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0068_auto_20210622_1659'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='haspermission',
            name='rlc_has_permission',
        ),
    ]
