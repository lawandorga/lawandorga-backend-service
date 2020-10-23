#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient
from django.utils import timezone
from unittest.mock import MagicMock
import datetime

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.permissions import (
    PERMISSION_VIEW_RECORDS_RLC,
    PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
)
from backend.static import error_codes
from backend.static.metrics import Metrics


class MetricsTest(TransactionTestCase):
    def setUp(self):
        self.base_url = "/api/records/record_deletion_requests/"
        self.process_url = "/api/records/process_record_deletion_request/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.client: APIClient = self.base_fixtures["users"][0]["client"]

    @staticmethod
    def get_value(lines: [str], key: str) -> float:
        for line in lines:
            if (
                line.find(key) != -1
                and line.find("HELP") == -1
                and line.find("TYPE") == -1
            ):
                return float(line.split(" ")[1])
        raise RuntimeError("value not found")

    @staticmethod
    def mock_datetime_now(hours, minutes, seconds=0):
        def now():
            return datetime.datetime(
                2020, 10, 13, hours, minutes, seconds, tzinfo=timezone.utc
            )

        return now

    @staticmethod
    def get_additional_rlc_users():
        rlc1 = api_models.Rlc(name="testrlc1", id=3004)
        rlc1.save()

        user11 = CreateFixtures.create_user(rlc1, "user11", "ad")
        user12 = CreateFixtures.create_user(rlc1, "user12", "ad")
        user13 = CreateFixtures.create_user(rlc1, "user13", "ad")

        rlc2 = api_models.Rlc(name="testrlc2", id=3006)
        rlc2.save()
        user21 = CreateFixtures.create_user(rlc2, "user21", "ad")
        user22 = CreateFixtures.create_user(rlc2, "user22", "ad")

        return [user11, user12, user13, user21, user22]

    def test_get_metrics(self):
        # Metrics.currently_active_users.set(3)
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")

        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 0,
        )

        # make sure first metrics was logged as session
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")

        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 0,
        )

    def test_get_user_activity(self):
        self.client.get("/api/profiles/")

        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")

        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 1,
        )

        self.base_fixtures["users"][1]["client"].get("/api/profiles/")
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")

        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 2,
        )

    def test_tmp(self):
        # datetime.datetime.now = self.tmp_mock
        timezone.now = MetricsTest.mock_datetime_now(1, 0)

        a = timezone.now()

        before = api_models.UserSession.objects.count()
        self.assertEqual(
            datetime.datetime(2012, 3, 1, 10, 0, 30, tzinfo=timezone.utc), a
        )
        self.base_fixtures["users"][1]["client"].get("/api/profiles/")
        after = api_models.UserSession.objects.count()
        self.assertEqual(before, 0)
        self.assertEqual(after, 1)

        session: api_models.UserSession = api_models.UserSession.objects.first()
        self.assertEqual(
            session.start_time,
            datetime.datetime(2012, 3, 1, 10, 0, 30, tzinfo=timezone.utc),
        )

    def test_user_session_timed_out(self):
        timezone.now = MetricsTest.mock_datetime_now(1, 0)
        self.base_fixtures["users"][0]["client"].get("/api/profiles/")
        timezone.now = MetricsTest.mock_datetime_now(1, 0, 20)
        self.base_fixtures["users"][0]["client"].get("/api/profiles/")
        timezone.now = MetricsTest.mock_datetime_now(1, 0, 30)
        self.base_fixtures["users"][0]["client"].get("/api/profiles/")

        sessions_count = api_models.UserSession.objects.count()
        self.assertEqual(sessions_count, 1)

        timezone.now = MetricsTest.mock_datetime_now(1, 50)
        self.base_fixtures["users"][0]["client"].get("/api/profiles/")

        sessions_count = api_models.UserSession.objects.count()
        self.assertEqual(sessions_count, 2)

        user_activity_paths = api_models.UserActivityPath.objects.count()
        self.assertEqual(user_activity_paths, 1)

        timezone.now = MetricsTest.mock_datetime_now(1, 50, 10)
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")
        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 1,
        )

        timezone.now = MetricsTest.mock_datetime_now(1, 50, 11)
        self.base_fixtures["users"][1]["client"].get("/api/profiles/")

        timezone.now = MetricsTest.mock_datetime_now(1, 50, 12)
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")
        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 2,
        )

    def test_different_rlc_metrics(self):
        timezone.now = MetricsTest.mock_datetime_now(1, 0)
        self.base_fixtures["users"][0]["client"].get("/api/profiles/")
        self.base_fixtures["users"][1]["client"].get("/api/profiles/")
        self.base_fixtures["users"][2]["client"].get("/api/profiles/")
        self.base_fixtures["users"][3]["client"].get("/api/profiles/")

        users = MetricsTest.get_additional_rlc_users()
        users[0]["client"].get("/api/profiles/")
        users[1]["client"].get("/api/profiles/")
        users[2]["client"].get("/api/profiles/")
        users[3]["client"].get("/api/profiles/")
        users[4]["client"].get("/api/profiles/")

        timezone.now = MetricsTest.mock_datetime_now(1, 0, 3)
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")
        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 9,
        )

        timezone.now = MetricsTest.mock_datetime_now(2, 0)
        self.base_fixtures["users"][0]["client"].get("/api/profiles/")
        self.base_fixtures["users"][1]["client"].get("/api/profiles/")
        self.base_fixtures["users"][2]["client"].get("/api/profiles/")
        users[0]["client"].get("/api/profiles/")
        users[1]["client"].get("/api/profiles/")
        users[3]["client"].get("/api/profiles/")

        timezone.now = MetricsTest.mock_datetime_now(2, 0, 3)
        response: Response = APIClient().get("/metrics")
        lines: [str] = response.content.decode("utf-8").split("\n")
        self.assertEqual(
            int(MetricsTest.get_value(lines, "currently_active_users")), 6,
        )

        # a = int(MetricsTest.get_value(lines, "currently_active_users_per_rlc"))
        # b = 1
