from core.mail_imports.use_cases.mail_import import (
    ErrorEmail,
    ValidatedEmail,
    assign_emails_to_folder_uuid,
)


def test_assign_emails_to_folder_uuid_works():
    emails = [
        ValidatedEmail(
            num="test",
            sender="test",
            to="test",
            cc="test",
            bcc="test",
            date="test",
            subject="test",
            content="test",
            addresses=[],
        ),
        ErrorEmail(num="test", error="test"),
    ]
    assigned = assign_emails_to_folder_uuid(emails)
    assert len(assigned) == 2
