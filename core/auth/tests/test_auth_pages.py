"""Rendering tests for the restyled auth pages. They check the accessibility
and autofill attributes of the templates. Login, 2FA and registration logic
are covered by the other tests in this folder."""

import pytest
from django.conf import settings
from django.test import Client

from core.auth.models.org_user import OrgUser
from core.auth.use_cases.mfa import create_mfa_secret, enable_mfa_secret
from core.legal.models import LegalRequirement
from core.org.models import Org
from core.tests import test_helpers

pytestmark = pytest.mark.django_db


def html_of(response) -> str:
    assert response.status_code == 200
    return response.content.decode("utf-8")


def test_login_page_renders_with_autocomplete_and_reset_info():
    html = html_of(Client().get("/auth/user/login/"))

    assert 'autocomplete="username"' in html
    assert 'autocomplete="current-password"' in html
    assert "What happens when I reset my password?" in html
    assert 'href="/auth/user/password_reset/"' in html
    assert 'role="alert"' not in html
    # the sentence about unlocking is not part of the error message
    assert "has to unlock your account first" not in html


def test_login_error_marks_fields_invalid_and_links_the_error_block():
    response = Client().post(
        "/auth/user/login/",
        {"username": "nobody@law-orga.de", "password": "wrong"},
    )
    html = html_of(response)

    assert 'role="alert"' in html
    assert 'id="form-errors"' in html
    assert html.count('aria-invalid="true"') == 2
    assert html.count('aria-describedby="form-errors"') == 2


def test_mfa_login_page_has_one_time_code_field():
    full_user = test_helpers.create_org_user()
    user: OrgUser = full_user["org_user"]  # type: ignore
    create_mfa_secret(user)
    enable_mfa_secret(user)
    client = Client()
    client.post(
        "/login/",
        {"username": user.email, "password": settings.DUMMY_USER_PASSWORD},
    )

    html = html_of(client.get("/auth/mfa/login/"))

    assert "Two-factor authentication" in html
    assert 'autocomplete="one-time-code"' in html
    assert 'inputmode="numeric"' in html


def test_register_page_keeps_native_select_and_adds_autocomplete():
    org = Org.objects.create(name="Law Clinic Musterstadt")
    lr = LegalRequirement.objects.create(
        title="Datenschutz", content="<p>Text</p>", accept_required=True
    )

    html = html_of(Client().get("/auth/user/register/"))

    # progressive enhancement: the native select is rendered and submitted
    assert "data-lo-combobox" in html
    assert '<select name="org"' in html
    assert 'value="{}"'.format(org.pk) in html
    assert 'autocomplete="name"' in html
    assert 'autocomplete="email"' in html
    assert html.count('autocomplete="new-password"') == 2
    assert 'href="/auth/user/register/legal-requirement/{}/"'.format(lr.pk) in html


def test_register_errors_are_shown_in_the_error_block():
    html = html_of(Client().post("/auth/user/register/", {}))

    assert 'role="alert"' in html
    assert 'aria-invalid="true"' in html
    assert 'aria-describedby="form-errors' in html


@pytest.mark.parametrize(
    "url",
    [
        "/auth/user/password_reset/",
        "/auth/user/password_reset_done/",
        "/auth/user/password_reset_complete/",
        "/auth/user/password_reset_confirm/abc/def/",
        "/auth/user/register/successful/",
    ],
)
def test_simple_auth_pages_render(url):
    html = html_of(Client().get(url))

    assert '<html lang="en">' in html
    assert "<main" in html
    assert "<header" in html


def test_password_reset_form_has_email_autocomplete():
    html = html_of(Client().get("/auth/user/password_reset/"))

    assert 'autocomplete="email"' in html
