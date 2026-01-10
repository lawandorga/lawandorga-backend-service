from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template import loader



class Command(BaseCommand):

    def handle(self, *args, **options):
        login_url = settings.MAIN_FRONTEND_URL
        deletion_date = "31.02.2026"
        test_user = {
            "name": "Muster",
            "inactive_years": 5,
            "email": "test@law-orga.de",
        }
        context = {
            "user": test_user,
            "login_url": login_url,
            "deletion_date": deletion_date,
        }

        subject = "Important: Your Law&Orga account is scheduled for deletion"
        message = (
            f"Dear {test_user['name']},\n\n"
            f"We noticed that you have not logged into your account for over {test_user['inactive_years']} years. "
            "As part of our commitment to data privacy and security, we regularly remove inactive accounts.\n\n"
            "Your account is scheduled to be deleted in 1 month.\n\n"
            f"If you wish to keep your account and all associated data, simply log in to your account before {deletion_date}.\n\n"
            f"Log in: {login_url}\n\n"
            "If you have any questions or need assistance, feel free to contact our support team.\n\n"
            "Thank you for being a part of our community.\n\n"
            "Best regards,\nThe Law&Orga Team"
        )
        html_message = loader.render_to_string(
            "email_templates/inactive_user.html", context
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_user["email"]],
            html_message=html_message,
        )
