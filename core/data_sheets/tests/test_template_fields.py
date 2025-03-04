from core.data_sheets.models.template import DataSheetTemplate
from core.data_sheets.use_cases.templates import (
    create_field,
    delete_field,
    update_field,
)
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES
from core.seedwork import test_helpers


def test_create_field(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        rlc=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "standard", "Standard Field", 1)
    assert len(template.fields) == 5


def test_update_field(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        rlc=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "standard", "Standard Field", 1)
    field = template.fields[0]
    assert field.name == "Standard Field"
    update_field(org_user, field.uuid, "Standard Field New", 5)
    assert template.fields[0].name == "Standard Field New"


def test_delete_field(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        rlc=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "standard", "Standard Field", 1)
    field = template.fields[0]
    delete_field(org_user, field.uuid, False)
