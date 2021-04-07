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

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.permissions import (
    PERMISSION_VIEW_RECORDS_RLC,
    PERMISSION_MANAGE_PERMISSIONS_RLC,
)
from backend.static import error_codes


class HasPermissionTest(TransactionTestCase):
    def setUp(self):
        self.base_url = "/api/has_permission/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(
            rlc=self.base_fixtures["rlc"], users=users
        )
        self.client: APIClient = self.base_fixtures["users"][0]["client"]
        self.private: bytes = self.base_fixtures["users"][0]["private"]

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_MANAGE_PERMISSIONS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

    def test_create_has_permission_invalid_permission(self):
        response: Response = self.base_fixtures["users"][2]["client"].post(
            self.base_url,
            {
                "permission": api_models.Permission.objects.first().id,
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(403, response.status_code)

    def test_create_has_permission_success(self):
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            number_of_has_permissions_before + 1,
            api_models.HasPermission.objects.count(),
        )

    def test_create_has_permission_wrong_post(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][0].id,
            },
        )
        self.assertEqual(400, response.status_code)

        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(400, response.status_code)

        response: Response = self.client.post(
            self.base_url,
            {
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(400, response.status_code)

    def test_create_has_permission_wrong_permission_id(self):
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        response: Response = self.client.post(
            self.base_url,
            {
                "permission": 234234,
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            number_of_has_permissions_before, api_models.HasPermission.objects.count(),
        )

    def test_create_has_permission_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_MANAGE_PERMISSIONS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": foreign_rlc_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
            format="json",
            **{"HTTP_PRIVATE_KEY": foreign_rlc_fixtures["users"][0]["private"]},
        )
        self.assertEqual(403, response.status_code)

    def test_create_has_permission_wrong_group_id(self):
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": 1231241,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
            format="json",
            **{"HTTP_PRIVATE_KEY": self.private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            number_of_has_permissions_before, api_models.HasPermission.objects.count(),
        )

    def test_create_has_permission_wrong_rlc_id(self):
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": 344234,
            },
            format="json",
            **{"HTTP_PRIVATE_KEY": self.private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            number_of_has_permissions_before, api_models.HasPermission.objects.count(),
        )

    def test_create_has_permission_doubled(self):
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(201, response.status_code)

        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][0].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__HAS_PERMISSION__ALREADY_EXISTING["error_code"],
            response.data["error_code"],
        )

        self.assertEqual(
            number_of_has_permissions_before + 1,
            api_models.HasPermission.objects.count(),
        )

    def test_create_has_permission_success_record_keys(self):
        number_of_record_keys_before: int = record_models.RecordEncryption.objects.count()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_MANAGE_PERMISSIONS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][2].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
            format="json",
            **{"HTTP_PRIVATE_KEY": self.private},
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            number_of_record_keys_before
            + record_models.EncryptedRecord.objects.count(),
            record_models.RecordEncryption.objects.count(),
        )

    def test_create_has_permission_no_private_key(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_MANAGE_PERMISSIONS_RLC
        )
        response: Response = self.client.post(
            self.base_url,
            {
                "permission": permission.id,
                "group_has_permission": self.base_fixtures["groups"][2].id,
                "permission_for_rlc": self.base_fixtures["rlc"].id,
            },
            format="json",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED["error_code"],
            response.data["error_code"],
        )

    def test_destroy_has_permission_success(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            group_has_permission=self.base_fixtures["groups"][1],
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        has_permission.save()
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        response: Response = self.client.delete(
            self.base_url + str(has_permission.id) + "/",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            number_of_has_permissions_before - 1,
            api_models.HasPermission.objects.count(),
        )

    def test_destroy_has_permission_no_permission(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            group_has_permission=self.base_fixtures["groups"][1],
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        has_permission.save()
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        response: Response = self.base_fixtures["users"][3]["client"].delete(
            self.base_url + str(has_permission.id) + "/",
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            number_of_has_permissions_before, api_models.HasPermission.objects.count(),
        )

    def test_destroy_has_permission_wrong_id(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            group_has_permission=self.base_fixtures["groups"][1],
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        has_permission.save()
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        response: Response = self.base_fixtures["users"][3]["client"].delete(
            self.base_url + "12312312/",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            number_of_has_permissions_before, api_models.HasPermission.objects.count(),
        )

    def test_destroy_has_permission_foreign_rlc(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission_not_to_be_deleted: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            group_has_permission=self.base_fixtures["groups"][1],
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        has_permission_not_to_be_deleted.save()

        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_MANAGE_PERMISSIONS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()
        number_of_has_permissions_before: int = api_models.HasPermission.objects.count()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].delete(
            self.base_url + str(has_permission_not_to_be_deleted.id) + "/"
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            number_of_has_permissions_before, api_models.HasPermission.objects.count()
        )


# TODO: really? success, record key permission, delete keys
