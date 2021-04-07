# Generated by Django 3.1.7 on 2021-03-24 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0046_auto_20210324_1705"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="forgotpasswordlinks",
            options={
                "verbose_name": "ForgotPasswordLink",
                "verbose_name_plural": "ForgotPasswordLinks",
            },
        ),
        migrations.AlterModelOptions(
            name="group",
            options={"verbose_name": "Group", "verbose_name_plural": "Groups"},
        ),
        migrations.AlterModelOptions(
            name="haspermission",
            options={
                "verbose_name": "HasPermission",
                "verbose_name_plural": "HasPermissions",
            },
        ),
        migrations.AlterModelOptions(
            name="missingrlckey",
            options={
                "verbose_name": "MissingRlcKey",
                "verbose_name_plural": "MissingRlcKeys",
            },
        ),
        migrations.AlterModelOptions(
            name="newuserrequest",
            options={
                "verbose_name": "NewUserRequest",
                "verbose_name_plural": "NewUserRequests",
            },
        ),
        migrations.AlterModelOptions(
            name="notification",
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
        migrations.AlterModelOptions(
            name="notificationgroup",
            options={
                "verbose_name": "NotificationGroup",
                "verbose_name_plural": "NotificationGroups",
            },
        ),
        migrations.AlterModelOptions(
            name="permission",
            options={
                "verbose_name": "Permission",
                "verbose_name_plural": "Permissions",
            },
        ),
        migrations.AlterModelOptions(
            name="rlc", options={"verbose_name": "Rlc", "verbose_name_plural": "Rlcs"},
        ),
        migrations.AlterModelOptions(
            name="rlcencryptionkeys",
            options={
                "verbose_name": "RlcEncryptionKey",
                "verbose_name_plural": "RlcEncryptionKeys",
            },
        ),
        migrations.AlterModelOptions(
            name="rlcsettings",
            options={
                "verbose_name": "RlcSetting",
                "verbose_name_plural": "RlcSettings",
            },
        ),
        migrations.AlterModelOptions(
            name="useractivitypath",
            options={
                "verbose_name": "UserActivityPath",
                "verbose_name_plural": "UserActivityPaths",
            },
        ),
        migrations.AlterModelOptions(
            name="userencryptionkeys",
            options={
                "verbose_name": "UserEncryptionKey",
                "verbose_name_plural": "UserEncryptionKeys",
            },
        ),
        migrations.AlterModelOptions(
            name="userprofile",
            options={
                "verbose_name": "UserProfile",
                "verbose_name_plural": "UserProfiles",
            },
        ),
        migrations.AlterModelOptions(
            name="usersession",
            options={
                "verbose_name": "UserSession",
                "verbose_name_plural": "UserSessions",
            },
        ),
        migrations.AlterModelOptions(
            name="usersessionpath",
            options={
                "verbose_name": "UserSessionPath",
                "verbose_name_plural": "UserSessionPaths",
            },
        ),
        migrations.AlterModelOptions(
            name="usersrlckeys",
            options={
                "verbose_name": "UserRlcKeys",
                "verbose_name_plural": "UsersRlcKeys",
            },
        ),
    ]
