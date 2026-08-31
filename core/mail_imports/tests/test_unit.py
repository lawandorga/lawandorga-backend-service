from email.message import Message

from core.mail_imports.use_cases.mail_import import (
    ErrorEmail,
    ValidatedEmail,
    assign_email_to_folder_uuid,
    get_date_from_message,
)


def test_assign_emails_to_folder_uuid_works():
    assigned1 = assign_email_to_folder_uuid(
        ValidatedEmail(
            uid="test",
            sender="test",
            to="test",
            cc="test",
            bcc="test",
            date="test",
            subject="test",
            content="test",
            addresses=[],
        )
    )
    assert isinstance(assigned1, ValidatedEmail)
    assigned2 = assign_email_to_folder_uuid(ErrorEmail(uid="test", error="test"))
    assert isinstance(assigned2, ErrorEmail)


def test_get_date_from_message_parses_rfc2822_date():
    message = Message()
    message["Date"] = "Sun, 23 Aug 2026 12:39:32 +0200"

    date = get_date_from_message(message)

    assert date == "2026-08-23 12:39:32+02:00"


def test_get_date_from_message_parses_encoded_quoted_date():
    message = Message()
    message["Date"] = "=?UTF-8?Q?=E2=80=9CSun,_23_Aug_2026_12:39:32_+0200=E2=80=9D?="

    date = get_date_from_message(message)

    assert date == "2026-08-23 12:39:32+02:00"
