import pytest
from django.test import Client
from django.utils import timezone

from core.internal.models import Article
from core.org.models import Org
from core.tests import test_helpers

pytestmark = pytest.mark.django_db


@pytest.fixture
def neighbourhood_user():
    org = Org.objects.create(name="Neighbourhood RLC")
    return test_helpers.create_org_user(org=org, email="neighbour@law-orga.de")


@pytest.fixture
def dummy_user():
    org = Org.objects.create(name="Dummy RLC")
    return test_helpers.create_org_user(org=org, email="dummy@law-orga.de")


def make_article(title, *recipient_orgs):
    article = Article.objects.create(
        title=title,
        preview="Preview",
        date=timezone.now().date(),
        content="Content",
    )
    if recipient_orgs:
        article.recipients.set(recipient_orgs)
    return article


def visible_article_ids(user):
    client = Client()
    client.login(**user)
    response = client.get("/api/internal/articles/dashboard/")
    return {article["id"] for article in response.json()}


def test_article_for_all_is_visible_to_all(neighbourhood_user, dummy_user):
    article = make_article("For All", neighbourhood_user["org"], dummy_user["org"])
    assert article.pk in visible_article_ids(neighbourhood_user)
    assert article.pk in visible_article_ids(dummy_user)


def test_article_for_nobody_is_visible_to_all(neighbourhood_user, dummy_user):
    article = make_article("For Nobody")
    assert article.pk in visible_article_ids(neighbourhood_user)
    assert article.pk in visible_article_ids(dummy_user)


def test_article_for_neighbourhood_only(neighbourhood_user, dummy_user):
    article = make_article("For Neighbourhood", neighbourhood_user["org"])
    assert article.pk in visible_article_ids(neighbourhood_user)
    assert article.pk not in visible_article_ids(dummy_user)


def test_article_for_dummy_only(neighbourhood_user, dummy_user):
    article = make_article("For Dummy", dummy_user["org"])
    assert article.pk not in visible_article_ids(neighbourhood_user)
    assert article.pk in visible_article_ids(dummy_user)
