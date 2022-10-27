import asyncio

from asgiref.sync import sync_to_async

from core.auth.models import RlcUser
from core.legal.models import LegalRequirement, LegalRequirementUser


async def create_legal_requirements_for_users() -> str:
    rlc_users = await sync_to_async(list)(RlcUser.objects.all())
    legal_requirements = await sync_to_async(list)(
        LegalRequirement.objects.prefetch_related("rlc_users").all()
    )

    created = 0
    statements = []
    for u in rlc_users:
        for lr in legal_requirements:
            lr_users = await sync_to_async(list)(lr.rlc_users.all())
            if u not in lr_users:
                statement = LegalRequirementUser.objects.acreate(  # type: ignore
                    rlc_user=u, legal_requirement=lr
                )
                statements.append(statement)
                created += 1

    await asyncio.gather(*statements)

    return "Created {} LegalRequirementUser objects.".format(created)
