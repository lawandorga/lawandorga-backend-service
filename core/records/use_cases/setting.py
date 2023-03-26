from core.auth.models.org_user import RlcUser
from core.records.models.setting import RecordsView
from core.seedwork.use_case_layer import use_case


@use_case
def create_view(__actor: RlcUser, name: str, columns: list[str]):
    view = RecordsView.create(name=name, user=__actor, columns=columns)
    view.save()
