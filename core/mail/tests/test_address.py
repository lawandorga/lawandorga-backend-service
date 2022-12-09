import pytest

from core.mail.models import MailAddress


def test_localpart_wrong_type():
    with pytest.raises(TypeError):
        MailAddress.check_localpart(213213)


def test_localpart_too_long():
    localpart = "".join(["a" for _ in range(0, 66)])
    with pytest.raises(ValueError):
        MailAddress.check_localpart(localpart)


def test_localpart_illegal_character():
    localpart = "dollarboy$$"
    with pytest.raises(ValueError):
        MailAddress.check_localpart(localpart)


def test_localpart_too_many_dots():
    localpart = "lenoardo.....von.gogh"
    with pytest.raises(ValueError):
        MailAddress.check_localpart(localpart)


def test_localpart_valid():
    MailAddress.check_localpart("max.muster")
    MailAddress.check_localpart("fraumuster")
    MailAddress.check_localpart("awesome_local-part")
