from core.mail_imports.use_cases.mail_import import (
    mark_email_as_pinned,
    mark_emails_as_read,
)

USECASES = {
    "mail_imports/mark_emails_as_read": mark_emails_as_read,
    "mail_imports/mark_email_as_pinned": mark_email_as_pinned,
}
