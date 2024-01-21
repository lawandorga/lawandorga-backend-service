from core.auth.models.org_user import OrgUser
from core.data_sheets.models.data_sheet import DataSheetEncryptionNew
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def delete_key(__actor: OrgUser, key_id: int):
    key = DataSheetEncryptionNew.objects.filter(user=__actor, pk=key_id).first()
    if key is None:
        raise UseCaseError(
            "The key you want to delete does not exist.",
        )
    if key.record.encryptions.filter(correct=True).count() <= 1:
        raise UseCaseError(
            "Not enough people have access to this record. "
            "There needs to be at least one person who must "
            "have access. You can not delete this key.",
        )
    if key.correct:
        raise UseCaseError("You can not delete a key that works.")
    key.delete()


@use_case
def test_keys(__actor: OrgUser):
    private_key_user = __actor.get_private_key()
    __actor.user.test_all_keys(private_key_user)
