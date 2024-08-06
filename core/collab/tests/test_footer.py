from uuid import uuid4

from core.collab.models.footer import Footer
from core.collab.models.template import Template
from core.collab.use_cases.footer import create_footer, delete_footer, update_footer
from core.seedwork import test_helpers


def test_create(db):
    user = test_helpers.create_org_user()["rlc_user"]
    uuid = uuid4()
    template = Template.create(user, uuid, "name", "description")
    template.save()
    create_footer(
        user,
        template.uuid,
        "column_1",
        "column_2",
        "column_3",
        "column_4",
    )
    assert user.org.footers.count() == 1


def test_update(db):
    user = test_helpers.create_org_user()["rlc_user"]
    footer = Footer.create(
        user.org_id,
        "column_1",
        "column_2",
        "column_3",
        "column_4",
    )
    footer.save()
    update_footer(
        user,
        footer.uuid,
        "column_1_updated",
        "column_2_updated",
        "column_3_updated",
        "column_4_updated",
    )
    footer.refresh_from_db()
    assert footer.column_1 == "column_1_updated"


def test_delete(db):
    user = test_helpers.create_org_user()["rlc_user"]
    footer = Footer.create(
        user.org_id,
        "column_1_updated",
        "column_2_updated",
        "column_3_updated",
        "column_4_updated",
    )
    footer.save()
    delete_footer(user, footer.uuid)
    assert user.org.footers.count() == 0
