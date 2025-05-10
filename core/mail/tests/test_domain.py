import pytest
from django.conf import settings

from core.mail.models import MailDomain
from core.seedwork.domain_layer import DomainError


def test_check_domain_wrong_type():
    with pytest.raises(TypeError):
        MailDomain.check_domain(234324)


def test_check_domain_illegal_start():
    with pytest.raises(DomainError):
        MailDomain.check_domain(".abc.de")
    with pytest.raises(DomainError):
        MailDomain.check_domain("-abc.de")
    with pytest.raises(DomainError):
        MailDomain.check_domain("+abc.de")


def test_check_domain_illegal_end():
    with pytest.raises(DomainError):
        MailDomain.check_domain("abc.de-")
    # with pytest.raises(DomainError):
    #     MailDomain.check_domain("abc.sdfadsfdasfdasf")
    with pytest.raises(DomainError):
        MailDomain.check_domain("abc.de.")


def test_check_domain_illegal_format():
    with pytest.raises(DomainError):
        MailDomain.check_domain("abc-.de")
    with pytest.raises(DomainError):
        MailDomain.check_domain("abc.$sdfadsfdasfdasf.com")


def test_domain_legal():
    MailDomain.check_domain("mail-test.law-orga.de")
    MailDomain.check_domain("law-orga.de")
    MailDomain.check_domain("abc.def.xyz.law-orga.de")
    MailDomain.check_domain("abc.def.xyz.law-orga.com")
    MailDomain.check_domain("law-orga.org")


def test_check_settings():
    domain = MailDomain(name="mail-abc.mydomain.de")
    correct_settings = {
        "MX": [f"20 {settings.MAIL_MX_RECORD}."],
        "SPF": [f"v=spf1 include:{settings.MAIL_SPF_RECORD} -all"],
        "DMARC": [f"{settings.MAIL_DMARC_RECORD}."],
        "DKIM": [f"{settings.MAIL_DKIM_RECORD}."],
    }
    result, error = domain.check_settings(correct_settings)
    assert result and domain.is_active


def test_wrong_settings():
    domain = MailDomain(name="mail-abc.mydomain.de")
    correct_settings = {
        "MX": [f"20 {settings.MAIL_MX_RECORD}."],
        "SPF": "the error is here",
        "DMARC": "none",
        "DKIM": "none",
    }
    result, error = domain.check_settings(correct_settings)
    assert result is False and not domain.is_active


def test_wrong_setting():
    domain = MailDomain(name="mail-abc.mydomain.de")
    correct_settings = {
        "MX": [f"20 {settings.MAIL_MX_RECORD}."],
        "SPF": ["my-wrong-setting"],
        "DMARC": [],
        "DKIM": [],
    }
    result, error = domain.check_settings(correct_settings)
    assert result is False and not domain.is_active and "my-wrong-setting" in error
