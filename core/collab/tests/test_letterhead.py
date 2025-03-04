from uuid import uuid4

from core.collab.models.letterhead import Letterhead
from core.collab.models.template import Template
from core.collab.use_cases.letterhead import (
    create_letterhead,
    delete_letterhead,
    update_letterhead,
)
from core.seedwork import test_helpers


def test_create(db):
    user = test_helpers.create_org_user()["org_user"]
    uuid = uuid4()
    template = Template.create(user, uuid, "name", "description")
    template.save()
    create_letterhead(
        user,
        template.uuid,
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "address_line_4",
        "address_line_5",
        "text_right",
    )
    assert user.org.letterheads.count() == 1


def test_update(db):
    user = test_helpers.create_org_user()["org_user"]
    lh = Letterhead.create(
        user.org_id,
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "address_line_4",
        "address_line_5",
        "text_right",
    )
    lh.save()
    update_letterhead(
        user,
        lh.uuid,
        "address_line_1_updated",
        "address_line_2_updated",
        "address_line_3_updated",
        "address_line_4_updated",
        "address_line_5_updated",
        "text_right_updated",
    )
    lh.refresh_from_db()
    assert lh.address_line_1 == "address_line_1_updated"


def test_delete(db):
    user = test_helpers.create_org_user()["org_user"]
    lh = Letterhead.create(
        user.org_id,
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "address_line_4",
        "address_line_5",
        "text_right",
    )
    lh.save()
    delete_letterhead(user, lh.uuid)
    assert user.org.letterheads.count() == 0
