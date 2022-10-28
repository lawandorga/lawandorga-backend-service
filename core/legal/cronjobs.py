from core.auth.models import RlcUser
from core.legal.models import LegalRequirement, LegalRequirementUser


def create_legal_requirements_for_users() -> str:
    rlc_users = list(RlcUser.objects.all())
    legal_requirements = list(
        LegalRequirement.objects.prefetch_related("rlc_users").all()
    )

    created = 0
    lrus = []
    for u in rlc_users:
        for lr in legal_requirements:
            lr_users = list(lr.rlc_users.all())
            if u not in lr_users:
                lru = LegalRequirementUser(rlc_user=u, legal_requirement=lr)
                lrus.append(lru)
                created += 1
    LegalRequirementUser.objects.bulk_create(lrus)

    return "Created {} LegalRequirementUser objects.".format(created)
