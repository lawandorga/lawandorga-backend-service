from django.core.management.base import BaseCommand

from core.mail_imports.models.mail_import import (
    ErrorEmail,
    MailInbox,
    ValidatedEmail,
    save_emails,
    validate_emails,
)

from seedwork.functional import list_filter


class Command(BaseCommand):
    help = "Importing Mails"

    def handle(self, *args, **options):
        with MailInbox() as mail_inbox:
            raw_emails = mail_inbox.get_raw_emails()
            self.stdout.write(f"Found {len(raw_emails)} emails")
            emails = validate_emails(raw_emails)
            self.stdout.write(f"Validated {len(emails)} emails")
            validated: list[ValidatedEmail] = list_filter(emails, lambda e: isinstance(e, ValidatedEmail))  # type: ignore
            self.stdout.write(f"{len(validated)} are valid")
            errors: list[ErrorEmail] = list_filter(emails, lambda e: isinstance(e, ErrorEmail))  # type: ignore
            self.stdout.write(f"{len(errors)} are invalid")
            save_emails(validated)
            self.stdout.write(f"Saved {len(validated)} emails")
            mail_inbox.delete_emails(validated)
            self.stdout.write(f"Deleted {len(validated)} emails")
            mail_inbox.mark_emails_as_error(errors)
            self.stdout.write(f"Marked {len(errors)} emails as error")
