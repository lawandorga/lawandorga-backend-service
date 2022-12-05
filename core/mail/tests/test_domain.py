import pytest

from core.mail.models import MailDomain


def test_check_domain_wrong_type():
    with pytest.raises(TypeError):
        MailDomain.check_domain(234324)


def test_check_domain_illegal_start():
    with pytest.raises(ValueError):
        MailDomain.check_domain(".abc.de")
    with pytest.raises(ValueError):
        MailDomain.check_domain("-abc.de")
    with pytest.raises(ValueError):
        MailDomain.check_domain("+abc.de")


def test_check_domain_illegal_end():
    with pytest.raises(ValueError):
        MailDomain.check_domain("abc.de-")
    with pytest.raises(ValueError):
        MailDomain.check_domain("abc.sdfadsfdasfdasf")
    with pytest.raises(ValueError):
        MailDomain.check_domain("abc.de.")


def test_check_domain_illegal_format():
    with pytest.raises(ValueError):
        MailDomain.check_domain("abc-.de")
    with pytest.raises(ValueError):
        MailDomain.check_domain("abc.$sdfadsfdasfdasf.com")


def test_domain_legal():
    MailDomain.check_domain("mail-test.law-orga.de")
    MailDomain.check_domain("law-orga.de")
    MailDomain.check_domain("abc.def.xyz.law-orga.de")
    MailDomain.check_domain("abc.def.xyz.law-orga.com")
    MailDomain.check_domain("law-orga.org")
