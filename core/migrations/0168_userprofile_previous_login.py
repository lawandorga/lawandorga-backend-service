from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0167_remove_calendareventshare_calendar_share_exactly_one_principal_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="previous_login",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
