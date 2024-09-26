from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.management.base import BaseCommand

from core.auth.models.org_user import OrgUser
from core.auth.token_generator import EmailConfirmationTokenGenerator


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user", nargs="+", type=str, help="User to check")
        parser.add_argument("token", nargs="+", type=str, help="Token to check")

    def handle(self, *args, **options):
        self.test_password_token(*args, **options)
        # self.test_email_token(*args, **options)

    def test_email_token(self, *args, **options):
        token = options["token"][0]
        rlc_user = OrgUser.objects.get(id=0)
        correct = EmailConfirmationTokenGenerator().check_token(rlc_user, token)
        self.stdout.write(f"Token is {'correct' if correct else 'incorrect'}")

    def test_password_token(self, *args, **options):
        token = options["token"][0]
        user = options["user"][0]
        rlc_user = OrgUser.objects.get(user__email=user)
        self.stdout.write(f"User: {rlc_user}")
        correct = PasswordResetTokenGenerator().check_token(rlc_user.user, token)
        self.stdout.write(f"Token is {'correct' if correct else 'incorrect'}")
