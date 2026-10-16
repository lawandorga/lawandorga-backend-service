import pytest

from core.data_sheets.models.template import DataSheetTemplate
from core.data_sheets.use_cases.templates import (
    create_field,
    delete_field,
    update_field,
)
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES
from core.seedwork.use_case_layer import UseCaseInputError
from core.tests import test_helpers


def test_create_field(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        org=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "Standard", "Standard Field", 1)
    assert len(template.fields) == 5


def test_create_field_rejects_order_above_integer_range(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        org=org_user.org, name="Record Template"
    )
    order = 2_147_483_648

    with pytest.raises(UseCaseInputError) as error:
        create_field(org_user, template.pk, "Standard", "Standard Field", order)

    assert error.value.param_errors == {
        "order": ["Order must be between 0 and 2147483647."]
    }


def test_update_field_rejects_order_above_integer_range(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        org=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "Standard", "Standard Field", 1)
    field = template.standard_fields.get(name="Standard Field")

    with pytest.raises(UseCaseInputError) as error:
        update_field(org_user, field.uuid, "Standard Field", 2_147_483_648)

    assert error.value.param_errors == {
        "order": ["Order must be between 0 and 2147483647."]
    }


def test_update_field(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        org=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "Standard", "Standard Field", 1)
    field = template.fields[0]
    assert field.name == "Standard Field"
    update_field(org_user, field.uuid, "Standard Field New", 5)
    assert template.fields[0].name == "Standard Field New"


def test_delete_field(db):
    user = test_helpers.create_org_user()
    org_user = user["org_user"]
    org_user.grant(PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES)
    template = DataSheetTemplate.objects.create(
        org=org_user.org, name="Record Template"
    )
    create_field(org_user, template.pk, "Standard", "Standard Field", 1)
    field = template.fields[0]
    delete_field(org_user, field.uuid, False)
