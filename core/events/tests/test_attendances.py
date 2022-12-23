import json
from datetime import datetime, timedelta

import pytest
from django.test import Client
from django.utils import timezone

from core.models import Org
from core.records.models import RecordTemplate
from core.seedwork import test_helpers as data
from ..models import Event, Attendance
from ..use_cases.attendances import create_attendance

from ...rlc.models import Permission
from ...static import PERMISSION_ADMIN_MANAGE_PERMISSIONS, PERMISSION_ADMIN_MANAGE_USERS


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def rlc_user(db, org):
    user = data.create_rlc_user(email="dummy@law-orga.de", rlc=org)
    yield user["rlc_user"]


def test_create_attendance(db, rlc_user):
    event = Event.objects.create(
        org=rlc_user.org,
        name="Test",
        start_time=timezone.now(),
        end_time=timezone.now()
    )
    create_attendance(rlc_user, "Y", event.id)
    assert Attendance.objects.filter(rlc_user=rlc_user, event=event, status="Y").exists()
