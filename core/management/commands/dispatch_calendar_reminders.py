from django.core.management.base import BaseCommand

from core.calendar.reminders import dispatch_due_reminders


class Command(BaseCommand):
    help = "Dispatch due calendar event reminders"

    def handle(self, *args, **options):
        result = dispatch_due_reminders()
        self.stdout.write(result)
