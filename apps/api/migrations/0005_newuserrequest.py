#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

# Generated by Django 2.1.2 on 2019-04-07 09:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_auto_20190212_0750"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewUserRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("requested", models.DateTimeField(auto_now_add=True)),
                ("processed_on", models.DateTimeField(null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("re", "requested"),
                            ("gr", "granted"),
                            ("de", "declined"),
                        ],
                        default="re",
                        max_length=2,
                    ),
                ),
                (
                    "request_from",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request_processed",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="new_user_permissions_processed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
