from django.core.management.base import BaseCommand

from core.calendar.reminders import send_due_reminders


class Command(BaseCommand):
    help = "Send due calendar event reminders"

    def handle(self, *args, **options):
        result = send_due_reminders()
        self.stdout.write(result)
