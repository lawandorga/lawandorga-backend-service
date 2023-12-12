from core.auth.models import MatrixUser, OrgUser
from core.seedwork.use_case_layer import use_case


@use_case
def create_matrix_user(__actor: OrgUser):
    user = MatrixUser.create(__actor.user)
    user.save()
