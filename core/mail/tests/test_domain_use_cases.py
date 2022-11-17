import pytest

from core.mail.use_cases.domain import add_domain
from core.seedwork.use_case_layer import UseCaseError


def test_add_domain(db, mail_user):
    add_domain(mail_user, 'law-orga.de')


def test_add_domain_exists_error(db, domain, mail_user):
    with pytest.raises(UseCaseError):
        add_domain(mail_user, domain.name)
