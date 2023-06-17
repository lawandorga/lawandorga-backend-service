from django.core.management.base import BaseCommand

from core.legal.models.legal_requirement import LegalRequirementEvent


class Command(BaseCommand):
    help = "Migrates Data"

    def handle(self, *args, **options):
        to_save = []
        for e in list(
            LegalRequirementEvent.objects.select_related(
                "actor_old",
                "legal_requirement_user",
                "legal_requirement_user__legal_requirement",
                "legal_requirement_user__rlc_user",
            )
        ):
            e.user = e.legal_requirement_user.rlc_user
            e.actor = e.actor_old.email if e.actor_old else ""
            e.legal_requirement = e.legal_requirement_user.legal_requirement
            to_save.append(e)
        LegalRequirementEvent.objects.bulk_update(
            to_save, ["user", "actor", "legal_requirement"]
        )
