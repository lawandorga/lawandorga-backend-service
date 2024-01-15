import pytest

from core.auth.use_cases.rlc_user import unlock_myself
from core.models import Org, OrgEncryption
from core.seedwork import test_helpers as data
from core.seedwork.use_case_layer import UseCaseError


def test_unlock_fails(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_org_user(rlc=rlc)
    rlc.generate_keys()
    data.create_data_sheet(users=[user_1["user"]])
    key = OrgEncryption.objects.get(user=user_1["user"])
    key.correct = False
    key.encrypted_key = b""
    key.save()
    with pytest.raises(UseCaseError):
        unlock_myself(user_1["rlc_user"])


def test_unlock_works(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_org_user(rlc=rlc)
    rlc.generate_keys()
    data.create_data_sheet(users=[user_1["user"]])
    rlc_user = user_1["rlc_user"]
    rlc_user.locked = True
    rlc_user.save()
    unlock_myself(rlc_user)
    rlc_user.refresh_from_db()
    assert rlc_user.locked is False
