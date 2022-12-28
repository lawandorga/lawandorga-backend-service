import pytest

from core.mail.use_cases.domain import add_domain, change_domain, check_domain_settings
from core.seedwork.use_case_layer import UseCaseError


def test_add_domain(db, mail_user):
    add_domain(mail_user, "law-orga.de")


def test_change_domain(db, domain, mail_user):
    change_domain(mail_user, "my-new-domain.com", domain.uuid)


def test_add_domain_exists_error(db, domain, mail_user):
    with pytest.raises(UseCaseError):
        add_domain(mail_user, domain.name)


def test_add_domain_invalid_domain(db, mail_user):
    with pytest.raises(ValueError):
        add_domain(mail_user, "domain.asdf$")


def test_change_domain_invalid_domain(db, domain, mail_user):
    with pytest.raises(ValueError):
        change_domain(mail_user, "domain.asdf$", domain.uuid)


def test_check_settings(db, domain, mail_user):
    result = check_domain_settings(
        mail_user, {"MX": "error", "DKIM": "", "DMARC": "", "SPF": ""}, domain.uuid
    )
    assert "error" in result
