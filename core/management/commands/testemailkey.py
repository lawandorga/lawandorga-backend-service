from django.core.management.base import BaseCommand

from core.auth.models.org_user import RlcUser
from core.auth.token_generator import EmailConfirmationTokenGenerator


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("token", nargs="+", type=str, help="Token to check")

    def handle(self, *args, **options):
        token = options["token"][0]
        rlc_user = RlcUser.objects.get(id=2574)
        EmailConfirmationTokenGenerator().check_token(rlc_user, token)
