from core.auth.models import MatrixUser, RlcUser
from core.seedwork.use_case_layer import use_case


@use_case
def create_matrix_user(__actor: RlcUser):
    user = MatrixUser.create(__actor.user)
    user.save()
