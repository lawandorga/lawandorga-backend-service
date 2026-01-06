from uuid import uuid4

from core.collab.models.template import Template
from core.collab.use_cases.template import (
    create_template,
    delete_template,
    update_template_description,
    update_template_name,
)
from core.tests import test_helpers


def test_create(db):
    user = test_helpers.create_org_user()["org_user"]
    uuid = uuid4()
    create_template(user, uuid, "name", "description")
    assert user.org.templates.count() == 1


def test_update_template_name(db):
    user = test_helpers.create_org_user()["org_user"]
    uuid = uuid4()
    template = Template.create(user, uuid, "name", "description")
    template.save()
    update_template_name(
        user,
        template.uuid,
        "name_updated",
    )
    template.refresh_from_db()
    assert template.name == "name_updated"


def test_update_template_description(db):
    user = test_helpers.create_org_user()["org_user"]
    uuid = uuid4()
    template = Template.create(user, uuid, "name", "description")
    template.save()
    template.save()
    update_template_description(
        user,
        template.uuid,
        "description_updated",
    )
    template.refresh_from_db()
    assert template.description == "description_updated"


def test_delete(db):
    user = test_helpers.create_org_user()["org_user"]
    uuid = uuid4()
    template = Template.create(user, uuid, "name", "description")
    template.save()
    delete_template(user, template.uuid)
    assert user.org.templates.count() == 0
