from apps.api.models import *
from apps.recordmanagement.models import *
from apps.api.management.commands.fixtures import Fixtures
from apps.files.models import *
from apps.api.tests.example_data import create


def aws_environment_variables_viable(command):
    if settings.SCW_SECRET_KEY:
        command.stdout.write("secret key: " + settings.SCW_SECRET_KEY, ending="")
    else:
        command.stdout.write("s3 secret key not found!")
        return False

    if settings.SCW_ACCESS_KEY:
        command.stdout.write("scw access key: " + settings.SCW_ACCESS_KEY, ending="")
    else:
        command.stdout.write("scw access key not found!")
        return False

    if settings.SCW_S3_BUCKET_NAME:
        command.stdout.write(
            "scw bucket name: " + settings.SCW_S3_BUCKET_NAME, ending=""
        )
    else:
        command.stdout.write("scw bucket name not found!")
        return False

    return True


def add_permissions():
    Fixtures.create_real_permissions_no_duplicates()
    Fixtures.create_real_folder_permissions_no_duplicate()
    Fixtures.create_real_collab_permissions()


def reset_db():
    UserProfile.objects.all().delete()
    OriginCountry.objects.all().delete()
    Group.objects.all().delete()
    HasPermission.objects.all().delete()
    Permission.objects.all().delete()
    Rlc.objects.all().delete()
    RecordDocumentTag.objects.all().delete()
    File.objects.all().delete()
    Folder.objects.all().delete()
    FolderPermission.objects.all().delete()
    PermissionForFolder.objects.all().delete()
    Notification.objects.all().delete()
    NotificationGroup.objects.all().delete()
    reset_db_encrypted()


def reset_db_encrypted():
    EncryptedClient.objects.all().delete()
    EncryptedRecord.objects.all().delete()
    EncryptedRecordPermission.objects.all().delete()
    EncryptedRecordMessage.objects.all().delete()
    EncryptedRecordDocument.objects.all().delete()
    EncryptedRecordDeletionRequest.objects.all().delete()

    UserEncryptionKeys.objects.all().delete()
    RlcEncryptionKeys.objects.all().delete()
    RecordEncryption.objects.all().delete()
    UsersRlcKeys.objects.all().delete()


def populate_deploy_db():
    Fixtures.create_real_origin_countries()
    add_permissions()


def create_dummy_data():
    create()
