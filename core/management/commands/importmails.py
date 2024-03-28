from django.core.management.base import BaseCommand

from core.folders.models import FoldersFolder
from core.mail_imports.models.mail_import import (
    ErrorEmail,
    MailInbox,
    ValidatedEmail,
    assign_emails,
    get_subset_of_emails,
    put_emails_in_folders,
    save_emails,
    validate_emails,
)

from seedwork.functional import list_filter


class Command(BaseCommand):
    help = "Importing Mails"

    def handle(self, *args, **options):
        foldersl = FoldersFolder.objects.values_list("uuid", "org_id")
        folders = {uuid: org_id for uuid, org_id in foldersl}

        with MailInbox() as mail_inbox:
            raw_emails = mail_inbox.get_raw_emails()
            self.stdout.write(f"|-- {len(raw_emails)} emails were found")

            emails = validate_emails(raw_emails)
            self.stdout.write(f"|-- {len(emails)} emails got checked")

            validated: list[ValidatedEmail] = list_filter(emails, lambda e: isinstance(e, ValidatedEmail))  # type: ignore
            self.stdout.write(f"  |-- {len(validated)} are valid")
            assigned = assign_emails(validated)
            self.stdout.write(f"    |-- {len(assigned)} emails are assigned")
            infolder = put_emails_in_folders(assigned, folders)
            self.stdout.write(f"    |-- {len(assigned)} emails are infolder")
            save_emails(infolder)
            self.stdout.write(f"      |-- {len(assigned)} emails got saved in django")
            mail_inbox.delete_emails(assigned)
            self.stdout.write(
                f"      |-- {len(assigned)} emails got deleted from inbox"
            )

            unassigned = get_subset_of_emails(validated, infolder)
            self.stdout.write(
                f"    |-- {len(unassigned)} emails are unassigned or not in folder"
            )
            mail_inbox.mark_emails_as_not_assignable(unassigned)
            self.stdout.write(
                f"      |-- {len(unassigned)} emails got marked as unassigned"
            )

            errors: list[ErrorEmail] = list_filter(emails, lambda e: isinstance(e, ErrorEmail))  # type: ignore
            self.stdout.write(f"  |-- {len(errors)} are invalid")
            mail_inbox.mark_emails_as_error(errors)
            self.stdout.write(f"    |-- Marked {len(errors)} emails as error")
