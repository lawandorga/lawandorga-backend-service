from django.core.management.base import BaseCommand

from core.auth.models.org_user import OrgUser
from core.auth.token_generator import EmailConfirmationTokenGenerator


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("token", nargs="+", type=str, help="Token to check")

    def handle(self, *args, **options):
        token = options["token"][0]
        rlc_user = OrgUser.objects.get(id=2757)
        correct = EmailConfirmationTokenGenerator().check_token(rlc_user, token)
        self.stdout.write(f"Token is {'correct' if correct else 'incorrect'}")
