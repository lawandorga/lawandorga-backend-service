from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0173_calendarlink"),
    ]

    operations = [
        migrations.AlterField(
            model_name="externallink",
            name="link",
            field=models.URLField(max_length=4096),
        ),
    ]
