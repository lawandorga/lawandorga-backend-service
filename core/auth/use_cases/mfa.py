from core.auth.models.mfa import MultiFactorAuthenticationSecret
from core.auth.models.org_user import RlcUser
from core.seedwork.use_case_layer import use_case


@use_case
def create_mfa_secret(__actor: RlcUser):
    mfa = MultiFactorAuthenticationSecret.create(user=__actor)
    mfa.save()


@use_case
def enable_mfa_secret(__actor: RlcUser):
    mfa = __actor.mfa_secret
    mfa.enable()
    mfa.save()
