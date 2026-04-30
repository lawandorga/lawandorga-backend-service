from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0162_rename_article_description_to_preview"),
    ]

    operations = [
        migrations.AddField(
            model_name="orguser",
            name="last_activity",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
