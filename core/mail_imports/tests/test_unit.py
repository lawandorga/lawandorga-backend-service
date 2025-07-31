from core.mail_imports.use_cases.mail_import import (
    ErrorEmail,
    ValidatedEmail,
    assign_email_to_folder_uuid,
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
