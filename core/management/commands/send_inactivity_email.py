from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template import loader
from django.utils import timezone

from core.auth.models.user import UserProfile

from seedwork.functional import list_filter, list_map


class Command(BaseCommand):

    def handle(self, *args, **options):
        login_url = settings.MAIN_FRONTEND_URL
        deletion_date = "14.04.2026"
        inactivity_years = 3
        three_years_ago = timezone.now() - timedelta(days=365 * inactivity_years)
        inactive_users = UserProfile.objects.filter(
            Q(last_login__lt=three_years_ago)
            | (Q(last_login__isnull=True) & Q(created__lt=three_years_ago))
        ).order_by("-pk")
        user_data = list_map(
            inactive_users,
            lambda u: {
                "pk": str(u.pk),
                "name": u.name,
                "inactive_years": "3",
                "email": u.email,
            },
        )
        already_sent = set()
        with open(
            settings.BASE_DIR + "/tmp/sent_inactivity_email.log", "r"
        ) as log_file:
            for line in log_file:
                already_sent.add(line.strip())
        user_data = list_filter(user_data, lambda u: u["email"] not in already_sent)

        for u in user_data:
            self.stdout.write(u["pk"])
            with open(
                settings.BASE_DIR + "/tmp/sent_inactivity_email.log", "a"
            ) as log_file:
                log_file.write(f"{u['email']}\n")
            context = {
                "user": u,
                "login_url": login_url,
                "deletion_date": deletion_date,
            }
            subject = "Important: Your Law&Orga account is scheduled for deletion"
            message = (
                f"Dear {u['name']},\n\n"
                f"We noticed that you have not logged into your account for over {u['inactive_years']} years. "
                "As part of our commitment to data privacy and security, we regularly remove inactive accounts.\n\n"
                f"Your account is scheduled to be deleted in 3 months ({deletion_date}).\n\n"
                f"If you wish to keep your account and all associated data, simply log in to your account before {deletion_date}.\n\n"
                f"Log in: {login_url}\n\n"
                "If you have any questions or need assistance, feel free to contact our support team.\n\n"
                "Thank you for being a part of our community.\n\n"
                "Best regards,\nThe Law&Orga Team"
            )
            html_message = loader.render_to_string(
                "email_templates/inactive_user.html", context
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[u["email"]],
                    html_message=html_message,
                )
            except Exception as e:
                print("ERROR:", e)
