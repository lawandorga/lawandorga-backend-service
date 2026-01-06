from django.test import Client

from core.data_sheets.models import DataSheetTemplate
from core.encryption.usecases import check_keys
from core.seedwork import test_helpers


def test_keys_check_fails(db):
    user_1 = test_helpers.create_raw_org_user(save=True)
    user_2 = test_helpers.create_raw_org_user(
        email="dummy2@law-orga.de", org=user_1.org
    )
    user_1.org.generate_keys()
    template = DataSheetTemplate.objects.create(org=user_1.org, name="Record Template")
    test_helpers.create_data_sheet(template=template, users=[user_1.user, user_2.user])
    test_helpers.create_data_sheet(template=template, users=[user_1.user, user_2.user])
    key = user_1.user.users_rlc_keys.get()
    key.encrypted_key = b"corrupted"
    key.save()
    assert key.correct

    check_keys(user_1)
    assert not user_1.user.users_rlc_keys.get().correct


def test_keys_check_works(db):
    user_1 = test_helpers.create_raw_org_user(save=True)
    user_2 = test_helpers.create_raw_org_user(
        email="dummy2@law-orga.de", org=user_1.org
    )
    user_1.org.generate_keys()
    template = DataSheetTemplate.objects.create(org=user_1.org, name="Record Template")
    test_helpers.create_data_sheet(template=template, users=[user_1.user, user_2.user])
    test_helpers.create_data_sheet(template=template, users=[user_1.user, user_2.user])
    check_keys(user_1)
    user_1.refresh_from_db()
    assert not user_1.locked


def test_org_keys_exist(db):
    user_1 = test_helpers.create_raw_org_user(save=True)
    user_1.org.generate_keys()
    assert user_1.user.users_rlc_keys.count()


def test_list_keys_works(db):
    user_1 = test_helpers.create_raw_org_user(save=True)
    user_2 = test_helpers.create_raw_org_user(
        email="dummy2@law-orga.de", org=user_1.org
    )
    user_1.org.generate_keys()
    template = DataSheetTemplate.objects.create(org=user_1.org, name="Record Template")
    test_helpers.create_data_sheet(template=template, users=[user_1.user, user_2.user])
    test_helpers.create_data_sheet(template=template, users=[user_1.user, user_2.user])
    c = Client()
    c.login(**user_1.login_data)  # type: ignore
    c.get("/api/auth/keys/")
