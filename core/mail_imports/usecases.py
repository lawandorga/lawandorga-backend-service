from core.mail_imports.use_cases.mail_import import (
    delete_mail,
    import_mails,
    mark_mails_as_read,
    mark_mails_as_unread,
    toggle_mail_pinned,
)

USECASES = {
    "mail_imports/mark_mails_as_read": mark_mails_as_read,
    "mail_imports/mark_mails_as_unread": mark_mails_as_unread,
    "mail_imports/toggle_mail_pinned": toggle_mail_pinned,
    "mail_imports/import_mails": import_mails,
    "mail_imports/delete_mail": delete_mail,
}
