import pytest
from django.test import Client

from core.models import Org
from core.org.models import ExternalLink
from core.org.use_cases.link import create_link, delete_link
from core.org.use_cases.org import accept_member_to_org
from core.permissions.static import PERMISSION_ADMIN_MANAGE_USERS
from core.seedwork import test_helpers as data


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def user(db, org):
    user = data.create_org_user(rlc=org)
    org.generate_keys()
    ExternalLink.objects.create(
        org=org, name="Test Link", link="https://www.amazon.de", order=1
    )
    yield user


def test_list_links_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/query/links/")
    response_data = response.json()
    assert response.status_code == 200 and len(response_data) == 1


def test_create_link_works(user, db):
    create_link(user["org_user"], "New Link", "https://law-orga.de", 2)
    assert ExternalLink.objects.filter(
        org=user["org_user"].org, name="New Link"
    ).exists()


def test_delete_link_works(user, db):
    link = user["org_user"].org.external_links.first()
    delete_link(user["org_user"], link.id)
    assert not ExternalLink.objects.filter(
        org=user["org_user"].org, id=link.id
    ).exists()


def test_member_accept(user, db):
    c = Client()
    c.login(**user)
    user["org_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    another_user = data.create_org_user(
        rlc=user["org_user"].org, email="another@law-orga.de"
    )
    accept_member_to_org(user["org_user"], another_user["org_user"].id)
    another_user["org_user"].refresh_from_db()
    assert another_user["org_user"].accepted
