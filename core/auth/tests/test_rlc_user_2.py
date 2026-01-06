import pytest

from core.auth.use_cases.org_user import unlock_myself
from core.models import Org, OrgEncryption
from core.seedwork.use_case_layer import UseCaseError
from core.tests import test_helpers as test_helpers


def test_unlock_fails(db):
    org = Org.objects.create(name="Test RLC")
    user_1 = test_helpers.create_org_user(org=org)
    org.generate_keys()
    test_helpers.create_data_sheet(users=[user_1["user"]])
    key = OrgEncryption.objects.get(user=user_1["user"])
    key.correct = False
    key.encrypted_key = b""
    key.save()
    with pytest.raises(UseCaseError):
        unlock_myself(user_1["org_user"])


def test_unlock_works(db):
    org = Org.objects.create(name="Test RLC")
    user_1 = test_helpers.create_org_user(org=org)
    org.generate_keys()
    test_helpers.create_data_sheet(users=[user_1["user"]])
    org_user = user_1["org_user"]
    org_user.locked = True
    org_user.save()
    unlock_myself(org_user)
    org_user.refresh_from_db()
    assert org_user.locked is False
