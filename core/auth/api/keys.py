from typing import List

from core.auth.api.schemas import InputKeyDelete, OutputKey
from core.auth.models import RlcUser
from core.records.models import RecordEncryptionNew
from core.seedwork.api_layer import ApiError, Router

router = Router()


# list keys
@router.api(output_schema=List[OutputKey])
def list_keys(rlc_user: RlcUser):
    return rlc_user.keys


# test keys
@router.post(url="test/", output_schema=List[OutputKey])
def command__test_keys(rlc_user: RlcUser):
    private_key_user = rlc_user.get_private_key()
    rlc_user.user.test_all_keys(private_key_user)
    return rlc_user.keys


# delete key
@router.delete(url="<int:id>/")
def delete_key(data: InputKeyDelete, rlc_user: RlcUser):
    key = RecordEncryptionNew.objects.filter(user=rlc_user, pk=data.id).first()
    if key is None:
        raise ApiError(
            "The key you want to delete does not exist.",
        )
    if key.record.encryptions.filter(correct=True).count() <= 1:
        raise ApiError(
            "Not enough people have access to this record. "
            "There needs to be at least one person who must "
            "have access. You can not delete this key.",
        )
    if key.correct:
        raise ApiError("You can not delete a key that works.")
    key.delete()
