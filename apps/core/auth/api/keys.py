from typing import List, Literal

from pydantic import BaseModel

from apps.core.models import UserProfile
from apps.recordmanagement.models import RecordEncryptionNew
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

router = Router()


# schemas
class Key(BaseModel):
    id: int
    correct: bool
    source: Literal["RECORD", "RLC"]
    information: str

    class Config:
        orm_mode = True


class KeyDelete(BaseModel):
    id: int


# list keys
LIST_KEYS_SUCCESS = "User {} has requested the list of all his keys."


@router.api(output_schema=List[Key], auth=True)
def list_keys(user: UserProfile):
    all_keys: List[Key] = user.get_all_keys()
    return ServiceResult(LIST_KEYS_SUCCESS, all_keys)


# test keys
TEST_KEYS_SUCCESS = "User {} has tested all his keys."


@router.api(url="test/", output_schema=List[Key], auth=True)
def test_keys(user: UserProfile, private_key_user: str):
    user.test_all_keys(private_key_user)
    all_keys: List[Key] = user.get_all_keys()
    return ServiceResult(TEST_KEYS_SUCCESS, all_keys)


# delete key
DELETE_KEY_ERROR_NOT_FOUND = "User {} tried to delete a key that could not be found."
DELETE_KEY_ERROR_NOT_ENOUGH = (
    "User {} tried to delete a record key that only one other person or nobody has."
)
DELETE_KEY_ERROR_WORKS = "User {} tried to delete a key that works."
DELETE_KEY_SUCCESS_RECORD = "User {} deleted a record key."


@router.api(url="<int:id>/", method="POST", input_schema=KeyDelete, auth=True)
def delete_key(data: KeyDelete, user: UserProfile):
    print(data)
    key = RecordEncryptionNew.objects.filter(user=user, pk=data.id).first()
    if key is None:
        return ServiceResult(
            DELETE_KEY_ERROR_NOT_FOUND,
            error="The key you want to delete does not exist.",
        )
    if key.record.encryptions.filter(correct=True).count() <= 1:
        return ServiceResult(
            DELETE_KEY_ERROR_NOT_ENOUGH,
            error="Not enough people have access to this record. "
            "There needs to be at least one person who must "
            "have access. You can not delete this key.",
        )
    if key.correct:
        return ServiceResult(
            DELETE_KEY_ERROR_WORKS, error="You can not delete a key that works."
        )
    key.delete()
    return ServiceResult(DELETE_KEY_SUCCESS_RECORD)
