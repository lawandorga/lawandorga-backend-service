from core.mail_imports.use_cases.mail_import import (
    mark_mail_as_pinned,
    mark_mails_as_read,
)

USECASES = {
    # check upload/usecases.py for the structure
    "mail_imports/mark_mails_as_read": mark_mails_as_read,
    "mail_imports/mark_mail_as_pinned": mark_mail_as_pinned,
}
