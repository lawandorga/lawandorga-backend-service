from random import choice, randint
from typing import List

from django.conf import settings

from core import static
from core.auth.domain.user_key import UserKey
from core.collab.models import CollabPermission
from core.files.models import FolderPermission
from core.files_new.models.encrypted_record_document import EncryptedRecordDocument
from core.fixtures import (
    create_collab_permissions,
    create_folder_permissions,
    create_permissions,
)
from core.models import (
    CollabDocument,
    Group,
    HasPermission,
    InternalUser,
    Permission,
    RlcUser,
    TextDocumentVersion,
    UserProfile,
)
from core.records.fixtures import create_default_record_template
from core.records.models import (
    EncryptedRecordMessage,
    QuestionnaireQuestion,
    QuestionnaireTemplate,
    Record,
    RecordEncryptedStandardEntry,
    RecordEncryptedStandardField,
    RecordEncryptionNew,
    RecordMultipleEntry,
    RecordMultipleField,
    RecordSelectEntry,
    RecordSelectField,
    RecordStandardEntry,
    RecordStandardField,
    RecordStateEntry,
    RecordStateField,
    RecordTemplate,
    RecordUsersEntry,
    RecordUsersField,
)
from core.rlc.models import Org
from core.seedwork.encryption import AESEncryption


# helpers
def add_permissions_to_group(group: Group, permission_name):
    HasPermission.objects.create(
        group_has_permission=group,
        permission=Permission.objects.get(name=permission_name),
    )


# create
def create_rlcs():
    rlc1 = Org.objects.create(
        name="Dummy RLC",
        id=3033,
    )
    rlc2 = Org.objects.create(
        name="Neighbourhood RLC",
        id=1,
    )
    return [rlc1, rlc2]


def create_users(rlc1, rlc2):
    users = [
        (
            "ludwig.maximilian@outlook.de",
            "Ludwig Maximilian",
            "1985-05-12",
            "01732421123",
            "Maximilianstrasse 12",
            "München",
            "80539",
        ),
        (
            "xxALIxxstone@hotmail.com",
            "Albert Einstein",
            "1879-3-14",
            "01763425656",
            "Blumengasse 23",
            "Hamburg",
            "83452",
        ),
        (
            "mariecurry53@hotmail.com",
            "Marie Curie",
            "1867-11-7",
            "0174565656",
            "Jungfernstieg 2",
            "Hamburg",
            "34264",
        ),
        (
            "max.mustermann@gmail.com",
            "Maximilian Gustav Mustermann",
            "1997-10-23",
            "0176349756",
            "Schlossallee 100",
            "Grünwald",
            "82031",
        ),
        (
            "petergustav@gmail.com",
            "Peter Klaus Gustav von Guttenberg",
            "1995-3-11",
            "01763423732",
            "Leopoldstrasse 31",
            "Muenchen",
            "80238",
        ),
        (
            "gabi92@hotmail.com",
            "Gabriele Schwarz",
            "1998-12-10",
            "0175647332",
            "Kartoffelweg 12",
            "Muenchen",
            "80238",
        ),
        (
            "rudi343@gmail.com",
            "Rudolf Mayer",
            "1996-5-23",
            "01534423732",
            "Barerstrasse 3",
            "Muenchen",
            "80238",
        ),
        (
            "lea.g@gmx.com",
            "Lea Glas",
            "1985-7-11",
            "01763222732",
            "Argentinische Allee 34",
            "Hamburg",
            "34264",
        ),
        (
            "butterkeks@gmail.com",
            "Bettina Rupprecht",
            "1995-10-11",
            "01765673732",
            "Ordensmeisterstrasse 56",
            "Hamburg",
            "34264",
        ),
        (
            "willi.B@web.de",
            "Willi Birne",
            "1997-6-15",
            "01763425555",
            "Grunewaldstrasse 45",
            "Hamburg",
            "34264",
        ),
        (
            "pippi.langstrumpf@gmail.com",
            "Pippi Langstumpf",
            "1981-7-22",
            "01766767732",
            "Muehlenstraße 12",
            "Muenchen",
            "80238",
        ),
    ]

    created_users = []
    for user_data in users:
        user = UserProfile.objects.create(
            email=user_data[0],
            name=user_data[1],
        )
        r = RlcUser(
            user=user,
            org=choice([rlc1, rlc2]),
            phone_number=user_data[3],
            street=user_data[4],
            city=user_data[5],
            postal_code=user_data[6],
            birthday=user_data[2],
        )
        r.generate_keys(settings.DUMMY_USER_PASSWORD)
        r.save()
        if r.org == rlc1:
            created_users.append(user)
    return created_users


def create_dummy_users(rlc: Org, dummy_password: str = "qwe123") -> List[UserProfile]:
    users = []

    # main user
    user = UserProfile.objects.create(
        name="Mr. Dummy", email="dummy@law-orga.de", is_superuser=True
    )
    user.set_password(dummy_password)
    user.save()
    r = RlcUser(user=user, accepted=True, pk=999, email_confirmed=True, org=rlc)
    r.generate_keys(dummy_password)
    r.save()
    for permission in Permission.objects.all():
        r.grant(permission=permission)
    InternalUser.objects.create(user=user)
    users.append(user)

    # other dummy users
    user = UserProfile.objects.create(
        name="Tester 1",
        email="tester1@law-orga.de",
    )
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    r = RlcUser(user=user, accepted=True, pk=1000, org=rlc)
    r.generate_keys(dummy_password)
    r.save()
    users.append(user)

    user = UserProfile.objects.create(name="Tester 2", email="tester2@law-orga.de")
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    r = RlcUser(user=user, pk=1001, accepted=True, org=rlc)
    r.generate_keys(dummy_password)
    r.save()
    users.append(user)

    # return
    return users


def create_inactive_user(rlc):
    user = UserProfile(
        name="Mr. Inactive",
        email="inactive@law-orga.de",
    )
    user.set_password("qwe123")
    user.save()
    r = RlcUser(user=user, org=rlc)
    r.generate_keys(settings.DUMMY_USER_PASSWORD)
    r.save()


def create_groups(rlc: Org, users: List[UserProfile]):
    # create users group
    users_group = Group.objects.create(
        from_rlc=rlc,
        name="Berater",
        visible=False,
        description="all users",
    )

    for i in range(0, randint(0, len(users))):
        users_group.members.add(users[i].rlc_user)

    # create ag group
    ag_group = Group.objects.create(
        from_rlc=rlc,
        name="AG Datenschutz",
        visible=True,
        description="DSGVO",
    )

    for i in range(0, randint(0, int(len(users) / 2))):
        ag_group.members.add(users[i].rlc_user)

    # return
    return [users_group, ag_group]


def create_admin_group(rlc: Org, main_user: UserProfile):
    # create admin group
    admin_group = Group.objects.create(
        from_rlc=rlc,
        name="Administratoren",
        visible=False,
        description="haben alle Berechtigungen",
    )
    admin_group.members.add(main_user.rlc_user)

    add_permissions_to_group(admin_group, static.PERMISSION_ADMIN_MANAGE_PERMISSIONS)
    add_permissions_to_group(admin_group, static.PERMISSION_ADMIN_MANAGE_GROUPS)
    add_permissions_to_group(
        admin_group, static.PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS
    )
    add_permissions_to_group(admin_group, static.PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    # return
    return admin_group


def create_records(users, rlc):
    tags = (
        RecordMultipleField.objects.filter(template__rlc=rlc, name="Tags")
        .first()
        .options
    )
    records = [
        (
            "2018-7-12",
            "2018-8-29T13:54:0+00:00",
            "AZ-123/18",
            "informationen zum asylrecht",
            "Closed",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2018-6-20",
            "2018-7-10T17:30:0+00:00",
            "AZ-124/18",
            "nicht abgeschlossen",
            "Open",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2018-8-22",
            "2018-8-22T18:30:0+00:00",
            "AZ-125/18",
            "auf Bescheid wartend",
            "Waiting",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2018-3-9",
            "2018-3-24T15:54:0+00:00",
            "AZ-126/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Closed",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2017-10-2T15:3:0+00:00",
            "AZ-127/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Closed",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2018-9-2T16:3:0+00:00",
            "AZ-128/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Waiting",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2018-1-12T16:3:0+00:00",
            "AZ-129/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Open",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2018-1-2T16:3:0+00:00",
            "AZ-130/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Closed",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2018-12-2T16:3:0+00:00",
            "AZ-131/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Waiting",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2018-10-2T16:3:0+00:00",
            "AZ-132/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "Open",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            "2017-9-10",
            "2018-10-2T16:3:0+00:00",
            "AZ-139/18",
            "zweite akte von client 0",
            "Open",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
    ]

    # 0 first contact date
    # 1 last contact date
    # 2 token
    # 3 official note
    # 4 state
    # 5 users
    # 6 tags

    template = RecordTemplate.objects.first()
    created_records = []
    for record in records:
        # create
        created_record = Record.objects.create(template=template)
        # first contact date
        field = RecordStandardField.objects.get(
            template=template, name="First contact date"
        )
        RecordStandardEntry.objects.create(
            record=created_record, field=field, value=record[0]
        )
        # last contact date
        field = RecordStandardField.objects.get(
            template=template, name="Last contact date"
        )
        RecordStandardEntry.objects.create(
            record=created_record, field=field, value=record[1]
        )
        # token
        field = RecordStandardField.objects.get(template=template, name="Token")
        RecordStandardEntry.objects.create(
            record=created_record, field=field, value=record[2]
        )
        # official note
        field = RecordStandardField.objects.get(template=template, name="Official Note")
        RecordStandardEntry.objects.create(
            record=created_record, field=field, value=record[3]
        )
        # state
        field = RecordStateField.objects.get(template=template, name="State")
        RecordStateEntry.objects.create(
            record=created_record, field=field, value=record[4]
        )
        # consultants
        field = RecordUsersField.objects.get(template=template, name="Consultants")
        entry = RecordUsersEntry.objects.create(record=created_record, field=field)
        entry.value.set([u.rlc_user for u in record[5]])
        # tags
        field = RecordMultipleField.objects.get(template=template, name="Tags")
        RecordMultipleEntry.objects.create(
            record=created_record, field=field, value=record[6]
        )

        # secure the record
        aes_key = AESEncryption.generate_secure_key()
        for user in set(record[5]):
            record_encryption = RecordEncryptionNew(
                user=user.rlc_user, record=created_record, key=aes_key
            )
            record_encryption.encrypt(user.get_public_key())
            record_encryption.save()

        # append to return
        created_records.append(created_record)

    # return
    return created_records


def create_informative_record(main_user, main_user_password, users, rlc):
    users = [main_user] + users

    # create the informative record
    template = RecordTemplate.objects.filter(rlc=rlc).first()
    record = Record.objects.create(template=template)
    record_users = [choice(users), main_user]
    aes_key = AESEncryption.generate_secure_key()
    for user in record_users:
        if not RecordEncryptionNew.objects.filter(
            user=user.rlc_user, record=record
        ).exists():
            record_encryption = RecordEncryptionNew(
                user=user.rlc_user, record=record, key=aes_key
            )
            record_encryption.encrypt(user.get_public_key())
            record_encryption.save()
    # first contact date
    field = RecordStandardField.objects.get(
        template=template, name="First contact date"
    )
    RecordStandardEntry.objects.create(record=record, field=field, value="2018-01-03")
    # last contact date
    field = RecordStandardField.objects.get(template=template, name="Last contact date")
    RecordStandardEntry.objects.create(
        record=record, field=field, value="2019-03-11T09:32:21"
    )
    # token
    field = RecordStandardField.objects.get(template=template, name="Token")
    RecordStandardEntry.objects.create(field=field, record=record, value="AZ-001/18")
    # state
    field = RecordStateField.objects.get(template=template, name="State")
    RecordStateEntry.objects.create(field=field, record=record, value="Open")
    # official note
    field = RecordStandardField.objects.get(template=template, name="Official Note")
    RecordStandardEntry.objects.create(
        field=field, record=record, value="Best record ever created."
    )
    # client name
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Client name"
    )
    entry = RecordEncryptedStandardEntry(field=field, record=record, value="Bibi Aisha")
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # client note
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Client Note"
    )
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="Auf der Flucht von Ehemann getrennt worden."
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # client phone
    field = RecordEncryptedStandardField.objects.get(template=template, name="Phone")
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="01793456542"
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # client birthday
    field = RecordStandardField.objects.get(template=template, name="Birthday")
    RecordStandardEntry.objects.create(field=field, record=record, value="1990-05-01")
    # client origin country
    field = RecordSelectField.objects.get(template=template, name="Origin Country")
    RecordSelectEntry.objects.create(record=record, field=field, value="Afghanistan")
    # note
    field = RecordEncryptedStandardField.objects.get(template=template, name="Note")
    entry = RecordEncryptedStandardEntry(
        field=field,
        record=record,
        value="Mandant moechte dass wir ihn vor Gericht vertreten. "
        "Das duerfen wir aber nicht. #RDG",
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # consultant team
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Consultant Team"
    )
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="Taskforce 417"
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # lawyer
    field = RecordEncryptedStandardField.objects.get(template=template, name="Lawyer")
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="RA Guenther-Klaus, Kiesweg 3"
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # related persons
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Related Persons"
    )
    entry = RecordEncryptedStandardEntry(
        field=field,
        record=record,
        value="Sozialarbeiter Apfel (Direkt in der Unterkunft)",
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # contact
    field = RecordEncryptedStandardField.objects.get(template=template, name="Contact")
    entry = RecordEncryptedStandardEntry(
        field=field,
        record=record,
        value="Mail: asksk1@beispiel.de,\n Telefon: 0800 444 55 444",
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # bamf token
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="BAMF Token"
    )
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="QRS-232/2018"
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # foreign token
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Foreign Token"
    )
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="Vor Gericht: FA93932-1320"
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # first correspondence
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="First Correspondence"
    )
    entry = RecordEncryptedStandardEntry(
        field=field,
        record=record,
        value="Hallo Liebes Team der RLC,\n ich habe folgendes Problem."
        "\nKoennt ihr mir helfen?\n Vielen Dank",
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # circumstances
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Circumstances"
    )
    entry = RecordEncryptedStandardEntry(
        field=field,
        record=record,
        value="Kam ueber die Balkanroute, Bruder auf dem Weg verloren, "
        "wenig Kontakt zu Familie.",
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # next steps
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Next Steps"
    )
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="Klage einreichen und gewinnen!"
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # status described
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Status described"
    )
    entry = RecordEncryptedStandardEntry(
        field=field,
        record=record,
        value="Auf Antwort wartend, anschliessend weitere Bearbeitung.",
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # additional facts
    field = RecordEncryptedStandardField.objects.get(
        template=template, name="Additional facts"
    )
    entry = RecordEncryptedStandardEntry(
        field=field, record=record, value="Hat noch nie ne Schweinshaxe gegessen."
    )
    entry.encrypt(aes_key_record=aes_key)
    entry.save()
    # tags
    field = RecordMultipleField.objects.get(template=template, name="Tags")
    RecordMultipleEntry.objects.create(
        record=record, field=field, value=[choice(field.options), choice(field.options)]
    )
    # consultants
    field = RecordUsersField.objects.get(template=template, name="Consultants")
    entry = RecordUsersEntry.objects.create(record=record, field=field)
    entry.value.set([u.rlc_user for u in record_users])

    # add some documents
    EncryptedRecordDocument.objects.create(
        name="7_1_19__pass.jpg",
        record=record,
        file_size=18839,
        created_on="2019-1-7",
    )
    EncryptedRecordDocument.objects.create(
        name="3_10_18__geburtsurkunde.pdf",
        record=record,
        file_size=488383,
        created_on="2018-10-3",
    )
    EncryptedRecordDocument.objects.create(
        name="3_12_18__Ablehnungbescheid.pdf",
        record=record,
        file_size=343433,
        created_on="2018-12-3",
    )
    EncryptedRecordDocument.objects.create(
        name="1_1_19__Klageschrift.docx",
        record=record,
        file_size=444444,
        created_on="2019-1-1",
    )

    # add some messages
    message1 = EncryptedRecordMessage(
        sender=main_user.rlc_user,
        record=record,
        created="2019-3-11T10:12:21+00:00",
        message="Bitte dringend die Kontaktdaten des Mandanten eintragen.",
    )
    message1.encrypt(main_user.rlc_user, main_user.get_private_key(main_user_password))
    message1.save()
    message2 = EncryptedRecordMessage(
        sender=choice(users).rlc_user,
        record=record,
        created="2019-3-12T9:32:21",
        message="Ist erledigt! Koennen wir uns morgen treffen um das zu besprechen?",
    )
    message2.encrypt(main_user.rlc_user, main_user.get_private_key(main_user_password))
    message2.save()
    message3 = EncryptedRecordMessage(
        sender=main_user.rlc_user,
        record=record,
        created="2019-3-12T14:7:21",
        message="Klar, einfach direkt in der Mittagspause in der Mensa.",
    )
    message3.encrypt(main_user.rlc_user, main_user.get_private_key(main_user_password))
    message3.save()
    message4 = EncryptedRecordMessage(
        sender=choice(users).rlc_user,
        record=record,
        created="2019-3-13T18:7:21",
        message="Gut, jetzt faellt mir aber auch nichts mehr ein.",
    )
    message4.encrypt(main_user.rlc_user, main_user.get_private_key(main_user_password))
    message4.save()

    # return
    return record


def create_questionnaire_templates(rlc):
    template = QuestionnaireTemplate.objects.create(
        name="Standard Questionnaire", rlc=rlc, notes="Just the usual."
    )
    QuestionnaireQuestion.objects.create(
        questionnaire=template, question="How old are you?", type="TEXTAREA"
    )
    QuestionnaireQuestion.objects.create(
        questionnaire=template, question="Please sign the pdf.", type="FILE"
    )
    QuestionnaireQuestion.objects.create(
        questionnaire=template, question="How tall are you?", type="TEXTAREA"
    )


def create_collab_document(
    user, rlc, path="/Document", content="<h1>Collab Document</h1>"
):
    cd = CollabDocument.objects.create(
        path=path,
        rlc=rlc,
    )
    tv = TextDocumentVersion(document=cd, content=content, quill=False)
    private_key_user = (
        UserKey.create_from_dict(user.rlc_user.key)
        .decrypt_self(settings.DUMMY_USER_PASSWORD)
        .key.get_private_key()
        .decode("utf-8")
    )
    aes_key_rlc = rlc.get_aes_key(user=user, private_key_user=private_key_user)
    tv.encrypt(aes_key_rlc=aes_key_rlc)
    tv.save()


def create_collab_documents(user, rlc):
    create_collab_document(user, rlc, path="Document 1")
    create_collab_document(user, rlc, path="Document 1/Document 1.1")
    create_collab_document(user, rlc, path="Document 1/Document 1.2")
    create_collab_document(user, rlc, path="Document 2")


def create() -> None:
    # fixtures
    create_permissions(Permission)
    create_collab_permissions(CollabPermission)
    create_folder_permissions(FolderPermission)
    # password
    dummy_password = settings.DUMMY_USER_PASSWORD
    # rlcs and fixtures
    rlc1, rlc2 = create_rlcs()
    create_default_record_template(rlc1)
    create_default_record_template(rlc2)
    # users
    dummy, *other_dummies = create_dummy_users(rlc1)
    users = create_users(rlc1, rlc2)
    create_inactive_user(rlc1)
    # rlc keys
    rlc1.generate_keys()
    rlc2.generate_keys()
    # groups
    create_groups(rlc1, users)
    create_admin_group(rlc1, dummy)
    # records
    create_records(list(users) + [dummy], rlc1)
    create_informative_record(dummy, dummy_password, users, rlc1)
    # questionnaire templates
    create_questionnaire_templates(rlc1)
    # collab
    create_collab_documents(dummy, rlc1)
