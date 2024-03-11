from core.mail_imports.use_cases.mail_import import (
    mark_mail_as_pinned,
    mark_mails_as_read,
)

USECASES = {
    "mail_imports/mark_mails_as_read": mark_mails_as_read,
    "mail_imports/mark_mail_as_pinned": mark_mail_as_pinned,
}
