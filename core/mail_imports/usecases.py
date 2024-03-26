from core.mail_imports.use_cases.mail_import import (
    mark_mails_as_read,
    toggle_mail_pinned,
)

USECASES = {
    # check upload/usecases.py for the structure
    "mail_imports/mark_mails_as_read": mark_mails_as_read,
    "mail_imports/toggle_mail_pinned": toggle_mail_pinned,
}
