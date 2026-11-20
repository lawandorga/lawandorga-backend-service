import pytest
from django.test import Client
from django.utils import timezone

from core.internal.models import Article
from core.org.models import Org
from core.tests import test_helpers

pytestmark = pytest.mark.django_db


@pytest.fixture
def member():
    org = Org.objects.create(name="Member RLC")
    return test_helpers.create_org_user(org=org, email="member@law-orga.de")


@pytest.fixture
def outsider():
    org = Org.objects.create(name="Outsider RLC")
    return test_helpers.create_org_user(org=org, email="outsider@law-orga.de")


def make_article(title, *recipient_orgs):
    article = Article.objects.create(
        title=title,
        preview="Preview",
        date=timezone.now().date(),
        content="Secret content",
    )
    if recipient_orgs:
        article.recipients.set(recipient_orgs)
    return article


def client_for(user=None):
    client = Client()
    if user is not None:
        client.login(**user)
    return client


def test_index_page_only_lists_public_articles(member):
    public = make_article("For everyone")
    targeted = make_article("For members", member["org"])

    response = client_for().get("/api/internal/pages/index/")

    assert response.status_code == 200
    ids = {a["id"] for a in response.json()["articles"]}
    assert public.pk in ids
    assert targeted.pk not in ids


def test_index_page_lists_no_targeted_articles_for_members(member):
    targeted = make_article("For members", member["org"])

    response = client_for(member).get("/api/internal/pages/index/")

    ids = {a["id"] for a in response.json()["articles"]}
    assert targeted.pk not in ids


def test_anonymous_can_read_public_article():
    article = make_article("For everyone")

    response = client_for().get(f"/api/internal/pages/article/{article.pk}/")

    assert response.status_code == 200
    assert response.json()["content"] == "Secret content"


def test_anonymous_can_not_read_targeted_article(member):
    article = make_article("For members", member["org"])

    response = client_for().get(f"/api/internal/pages/article/{article.pk}/")

    assert response.status_code == 404
    assert b"Secret content" not in response.content


def test_member_of_recipient_org_can_read_targeted_article(member):
    article = make_article("For members", member["org"])

    response = client_for(member).get(f"/api/internal/pages/article/{article.pk}/")

    assert response.status_code == 200
    assert response.json()["id"] == article.pk


def test_member_of_other_org_can_not_read_targeted_article(member, outsider):
    article = make_article("For members", member["org"])

    response = client_for(outsider).get(f"/api/internal/pages/article/{article.pk}/")

    assert response.status_code == 404


def test_member_whose_login_is_not_allowed_is_treated_as_anonymous(member):
    article = make_article("For members", member["org"])
    org_user = member["org_user"]
    org_user.is_active = False
    org_user.save()

    response = client_for(member).get(f"/api/internal/pages/article/{article.pk}/")

    assert response.status_code == 404


def test_article_for_several_orgs_is_not_duplicated(member, outsider):
    article = make_article("For two orgs", member["org"], outsider["org"])

    assert Article.objects.visible_to(member["org"]).filter(pk=article.pk).count() == 1
    assert not Article.objects.public().filter(pk=article.pk).exists()
