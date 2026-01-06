from django.core import mail
from django.test import Client
from django.urls import reverse

from core.auth.models import OrgUser
from core.tests import test_helpers


def test_password_reset_works(db):
    # setup
    org = test_helpers.create_org()["org"]
    org_user = test_helpers.create_org_user(org=org)
    org.generate_keys()
    c = Client()

    # step1: open the password reset page
    response_1 = c.get(reverse("password_reset"))
    assert 200 == response_1.status_code

    # step2: submit the email on the password reset page and assert email was sent
    response_2 = c.post(
        reverse("password_reset"), {"email": org_user["org_user"].user.email}
    )
    context = response_2.context
    response_3 = c.get(response_2.url)
    assert "Check your inbox" in response_3.content.decode()
    assert 1 == len(mail.outbox)

    # step3: click the link within the email and submit new passwords
    token = context[0]["token"]
    uid = context[0]["uid"]
    url = reverse("password_reset_confirm", kwargs={"token": token, "uidb64": uid})
    response_4 = c.get(url, follow=True)
    assert "Set a new password" in response_4.content.decode()
    url = reverse(
        "password_reset_confirm", kwargs={"token": "set-password", "uidb64": uid}
    )
    response_5 = c.post(
        url, {"new_password1": "pass1234!", "new_password2": "pass1234!"}, follow=True
    )

    # step4: check that the complete page renders
    assert "Password reset complete" in response_5.content.decode()

    # check org user is locked but his keys work
    updated_org_user = OrgUser.objects.get(pk=org_user["org_user"].pk)
    assert updated_org_user.locked
    updated_org_user.keyring.get_encryption_key()
