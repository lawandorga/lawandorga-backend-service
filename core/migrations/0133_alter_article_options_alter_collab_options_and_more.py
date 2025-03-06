# Generated by Django 5.1.6 on 2025-03-06 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0132_alter_task_deadline"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="article",
            options={
                "ordering": ["-date"],
                "verbose_name": "INT_Article",
                "verbose_name_plural": "INT_Articles",
            },
        ),
        migrations.AlterModelOptions(
            name="collab",
            options={
                "verbose_name": "COL_Collab",
                "verbose_name_plural": "COL_Collabs",
            },
        ),
        migrations.AlterModelOptions(
            name="customsession",
            options={
                "verbose_name": "AUTH_CustomSession",
                "verbose_name_plural": "AUTH_CustomSessions",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheet",
            options={
                "ordering": ["-created"],
                "verbose_name": "DAT_DataSheet",
                "verbose_name_plural": "DAT_DataSheets",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetencryptedfileentry",
            options={
                "verbose_name": "DAT_DataSheetEncryptedFileEntry",
                "verbose_name_plural": "DAT_DataSheetEncryptedFileEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetencryptedfilefield",
            options={
                "verbose_name": "DAT_DataSheetEncryptedFileField",
                "verbose_name_plural": "DAT_DataSheetEncryptedFileField",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetencryptedselectentry",
            options={
                "verbose_name": "DAT_DataSheetEncryptedSelectEntry",
                "verbose_name_plural": "DAT_DataSheetEncryptedSelectEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetencryptedselectfield",
            options={
                "verbose_name": "DAT_DataSheetEncryptedSelectField",
                "verbose_name_plural": "DAT_DataSheetEncryptedSelectFields",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetencryptedstandardentry",
            options={
                "verbose_name": "DAT_DataSheetEncryptedStandardEntry",
                "verbose_name_plural": "DAT_DataSheetEncryptedStandardEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetencryptedstandardfield",
            options={
                "verbose_name": "DAT_DataSheetEncryptedStandardField",
                "verbose_name_plural": "DAT_DataSheetEncryptedStandardField",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetmultipleentry",
            options={
                "verbose_name": "DAT_DataSheetMultipleEntry",
                "verbose_name_plural": "DAT_DataSheetMultipleEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetmultiplefield",
            options={
                "verbose_name": "DAT_RecordMultipleField",
                "verbose_name_plural": "DAT_RecordMultipleFields",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetselectentry",
            options={
                "verbose_name": "DAT_DataSheetSelectEntry",
                "verbose_name_plural": "DAT_DataSheetSelectEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetselectfield",
            options={
                "verbose_name": "DAT_RecordSelectField",
                "verbose_name_plural": "DAT_RecordSelectFields",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetstandardentry",
            options={
                "verbose_name": "DAT_DataSheetStandardEntry",
                "verbose_name_plural": "DAT_DataSheetStandardEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetstandardfield",
            options={
                "verbose_name": "DAT_DataSheetStandardField",
                "verbose_name_plural": "DAT_DataSheetStandardField",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetstateentry",
            options={
                "verbose_name": "DAT_DataSheetStateEntry",
                "verbose_name_plural": "DAT_DataSheetStateEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetstatefield",
            options={
                "verbose_name": "DAT_RecordStateField",
                "verbose_name_plural": "DAT_RecordStateFields",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetstatisticentry",
            options={
                "verbose_name": "DAT_DataSheetStatisticEntry",
                "verbose_name_plural": "DAT_DataSheetStatisticEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetstatisticfield",
            options={
                "verbose_name": "DAT_DataSheetStatisticField",
                "verbose_name_plural": "DAT_DataSheetStatisticField",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheettemplate",
            options={
                "verbose_name": "DAT_RecordTemplate",
                "verbose_name_plural": "DAT_RecordTemplates",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetusersentry",
            options={
                "verbose_name": "DAT_DataSheetUsersEntry",
                "verbose_name_plural": "DAT_DataSheetUsersEntries",
            },
        ),
        migrations.AlterModelOptions(
            name="datasheetusersfield",
            options={
                "verbose_name": "DAT_RecordUsersField",
                "verbose_name_plural": "DAT_RecordUsersFields",
            },
        ),
        migrations.AlterModelOptions(
            name="encryptedrecorddocument",
            options={
                "verbose_name": "FIN_EncryptedRecordDocument",
                "verbose_name_plural": "FIN_EncryptedRecordDocuments",
            },
        ),
        migrations.AlterModelOptions(
            name="encryptedrecordmessage",
            options={
                "ordering": ["created"],
                "verbose_name": "MES_RecordMessage",
                "verbose_name_plural": "MES_RecordMessages",
            },
        ),
        migrations.AlterModelOptions(
            name="eventsevent",
            options={"ordering": ["start_time"], "verbose_name": "EVT_EventsEvents"},
        ),
        migrations.AlterModelOptions(
            name="file",
            options={
                "ordering": ["exists", "-created"],
                "verbose_name": "FIL_File",
                "verbose_name_plural": "FIL_Files",
            },
        ),
        migrations.AlterModelOptions(
            name="folder",
            options={
                "verbose_name": "FIL_Folder",
                "verbose_name_plural": "FIL_Folders",
            },
        ),
        migrations.AlterModelOptions(
            name="folderpermission",
            options={
                "verbose_name": "FIL_FolderPermission",
                "verbose_name_plural": "FIL_FolderPermissions",
            },
        ),
        migrations.AlterModelOptions(
            name="footer",
            options={
                "verbose_name": "COL_Footer",
                "verbose_name_plural": "COL_Footers",
            },
        ),
        migrations.AlterModelOptions(
            name="haspermission",
            options={
                "verbose_name": "PER_HasPermission",
                "verbose_name_plural": "PER_HasPermissions",
            },
        ),
        migrations.AlterModelOptions(
            name="helppage",
            options={
                "verbose_name": "INT_HelpPage",
                "verbose_name_plural": "INT_HelpPage",
            },
        ),
        migrations.AlterModelOptions(
            name="imprintpage",
            options={
                "verbose_name": "INT_ImprintPage",
                "verbose_name_plural": "INT_ImprintPage",
            },
        ),
        migrations.AlterModelOptions(
            name="indexpage",
            options={
                "verbose_name": "INT_IndexPage",
                "verbose_name_plural": "INT_IndexPage",
            },
        ),
        migrations.AlterModelOptions(
            name="letterhead",
            options={
                "verbose_name": "COL_Letterhead",
                "verbose_name_plural": "COL_Letterheads",
            },
        ),
        migrations.AlterModelOptions(
            name="loggedpath",
            options={
                "ordering": ["-time"],
                "verbose_name": "OTH_LoggedPath",
                "verbose_name_plural": "OTH_LoggedPaths",
            },
        ),
        migrations.AlterModelOptions(
            name="mailaccount",
            options={
                "verbose_name": "MAIL_MailAccount",
                "verbose_name_plural": "MAIL_MailAccounts",
            },
        ),
        migrations.AlterModelOptions(
            name="mailaddress",
            options={
                "ordering": ["localpart"],
                "verbose_name": "MAIL_MailAddress",
                "verbose_name_plural": "MAIL_MailAddress",
            },
        ),
        migrations.AlterModelOptions(
            name="mailadmin",
            options={
                "verbose_name": "MAIL_MailAdmin",
                "verbose_name_plural": "MAIL_MailAdmins",
            },
        ),
        migrations.AlterModelOptions(
            name="maildomain",
            options={
                "verbose_name": "MAIL_MailDomain",
                "verbose_name_plural": "MAIL_MailDomains",
            },
        ),
        migrations.AlterModelOptions(
            name="mailgroup",
            options={
                "verbose_name": "MAIL_MailGroup",
                "verbose_name_plural": "MAIL_MailGroups",
            },
        ),
        migrations.AlterModelOptions(
            name="mailorg",
            options={
                "verbose_name": "MAIL_MailOrg",
                "verbose_name_plural": "MAIL_MailOrgs",
            },
        ),
        migrations.AlterModelOptions(
            name="mailuser",
            options={
                "verbose_name": "MAIL_MailUser",
                "verbose_name_plural": "MAIL_MailUsers",
            },
        ),
        migrations.AlterModelOptions(
            name="permission",
            options={
                "ordering": ["name"],
                "verbose_name": "PER_Permission",
                "verbose_name_plural": "PER_Permissions",
            },
        ),
        migrations.AlterModelOptions(
            name="permissionforfolder",
            options={
                "verbose_name": "FIL_PermissionForFolder",
                "verbose_name_plural": "FIL_PermissionsForFolders",
            },
        ),
        migrations.AlterModelOptions(
            name="recordsaccessrequest",
            options={
                "ordering": ["-created"],
                "verbose_name": "REC_RecordsAccessRequest",
                "verbose_name_plural": "REC_RecordsAccessRequestes",
            },
        ),
        migrations.AlterModelOptions(
            name="recordsdeletion",
            options={
                "ordering": ["-created"],
                "verbose_name": "REC_RecordDeletion",
                "verbose_name_plural": "REC_RecordDeletions",
            },
        ),
        migrations.AlterModelOptions(
            name="recordsrecord",
            options={
                "verbose_name": "REC_RecordsRecord",
                "verbose_name_plural": "REC_RecordsRecords",
            },
        ),
        migrations.AlterModelOptions(
            name="recordsview",
            options={
                "ordering": ["-org", "ordering"],
                "verbose_name": "REC_RecordsView",
                "verbose_name_plural": "REC_RecordsViews",
            },
        ),
        migrations.AlterModelOptions(
            name="roadmapitem",
            options={
                "ordering": ["date"],
                "verbose_name": "INT_RoadmapItem",
                "verbose_name_plural": "INT_RoadmapItems",
            },
        ),
        migrations.AlterModelOptions(
            name="task",
            options={"verbose_name": "TAS_Task", "verbose_name_plural": "TAS_Tasks"},
        ),
        migrations.AlterModelOptions(
            name="template",
            options={
                "verbose_name": "COL_Template",
                "verbose_name_plural": "COL_Templates",
            },
        ),
        migrations.AlterModelOptions(
            name="tomspage",
            options={
                "verbose_name": "INT_TomsPage",
                "verbose_name_plural": "INT_TomsPage",
            },
        ),
        migrations.AlterModelOptions(
            name="uploadfile",
            options={
                "verbose_name": "UPL_UploadFile",
                "verbose_name_plural": "UPL_UploadFiles",
            },
        ),
        migrations.AlterModelOptions(
            name="uploadlink",
            options={
                "verbose_name": "UPL_UploadLink",
                "verbose_name_plural": "UPL_UploadLinks",
            },
        ),
    ]
