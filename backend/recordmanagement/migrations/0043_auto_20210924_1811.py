# Generated by Django 3.1.6 on 2021-09-24 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_remove_haspermission_rlc_has_permission'),
        ('recordmanagement', '0042_auto_20210924_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='rlc',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='api.rlc'),
        ),
    ]