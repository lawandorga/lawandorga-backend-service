from typing import List

from apps.core.auth.api.schemas import InputKeyDelete, OutputKey
from apps.core.auth.models import RlcUser
from apps.core.records.models import RecordEncryptionNew
from apps.seedwork.api_layer import ApiError, Router

router = Router()


# list keys
@router.api(output_schema=List[OutputKey], auth=True)
def list_keys(rlc_user: RlcUser):
    all_keys: List[OutputKey] = rlc_user.user.get_all_keys()
    return all_keys


# test keys
@router.post(url="test/", output_schema=List[OutputKey], auth=True)
def test_keys(rlc_user: RlcUser, private_key_user: str):
    rlc_user.user.test_all_keys(private_key_user)
    all_keys: List[OutputKey] = rlc_user.user.get_all_keys()
    return all_keys


# delete key
@router.delete(url="<int:id>/", input_schema=InputKeyDelete, auth=True)
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
