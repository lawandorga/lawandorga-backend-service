import pytest
from django.conf import settings
from django.test import Client

from core.models import UserProfile
from core.org.models import Group, Org
from core.auth.models import OrgUser
from core.permissions.models import HasPermission, Permission


@pytest.mark.django_db
def test_query_permissions_filters_by_user_id():
    """Should return fewer permissions when user_id is provided vs without."""
    # Create org and user
    org = Org.objects.create(name="Test RLC")
    user_profile = UserProfile.objects.create(email="testuser@law-orga.de", name="Test User")
    user_profile.set_password(settings.DUMMY_USER_PASSWORD)
    user_profile.save()

    org_user = OrgUser(user=user_profile, email_confirmed=True, accepted=True, org=org)
    org_user.generate_keys(settings.DUMMY_USER_PASSWORD)
    org_user.save()

    # Get the first permission and assign it to the user
    all_permissions = Permission.objects.all()
    perm_to_assign = all_permissions[0]
    HasPermission.objects.create(user=org_user, permission=perm_to_assign)

    # Query all permissions
    client = Client()
    response_all = client.get("/api/permissions/query/permissions/")
    assert response_all.status_code == 200
    all_result = response_all.json()

    # Query available permissions for this user
    response_filtered = client.get(f"/api/permissions/query/permissions/?user_id={org_user.pk}")
    assert response_filtered.status_code == 200
    filtered_result = response_filtered.json()

    # The filtered result should have fewer permissions
    assert len(filtered_result) < len(all_result), \
        f"Filtered ({len(filtered_result)}) should be less than all ({len(all_result)})"

    # The assigned permission should NOT be in the filtered result
    result_ids = {p["id"] for p in filtered_result}
    assert perm_to_assign.pk not in result_ids, \
        f"Assigned permission {perm_to_assign.pk} should not be in filtered results"


@pytest.mark.django_db
def test_query_permissions_filters_by_group_id():
    """Should return fewer permissions when group_id is provided vs without."""
    # Create org and group
    org = Org.objects.create(name="Test RLC 2")
    group = Group.objects.create(name="Test Group", org=org)

    # Get the first permission and assign it to the group
    all_permissions = Permission.objects.all()
    perm_to_assign = all_permissions[0]
    HasPermission.objects.create(group_has_permission=group, permission=perm_to_assign)

    # Query all permissions
    client = Client()
    response_all = client.get("/api/permissions/query/permissions/")
    assert response_all.status_code == 200
    all_result = response_all.json()

    # Query available permissions for this group
    response_filtered = client.get(f"/api/permissions/query/permissions/?group_id={group.pk}")
    assert response_filtered.status_code == 200
    filtered_result = response_filtered.json()

    # The filtered result should have fewer permissions
    assert len(filtered_result) < len(all_result), \
        f"Filtered ({len(filtered_result)}) should be less than all ({len(all_result)})"

    # The assigned permission should NOT be in the filtered result
    result_ids = {p["id"] for p in filtered_result}
    assert perm_to_assign.pk not in result_ids, \
        f"Assigned permission {perm_to_assign.pk} should not be in filtered results"
