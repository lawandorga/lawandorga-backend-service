#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2021  Dominik Walser
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

from django.db.utils import IntegrityError
from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api.models import HasPermission, Permission
from backend.collab.models import (
    CollabDocument,
    PermissionForCollabDocument,
    CollabPermission,
)
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.static.permissions import PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC


class PermissionForCollabDocumentModelTest(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()

    def test_save_doubled_permission(self):
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        permission = CollabPermission.objects.create(name="test_permission")

        permission_data = {
            "document": document,
            "group_has_permission": self.base_fixtures["groups"][0],
            "permission": permission,
        }

        PermissionForCollabDocument.objects.create(**permission_data)
        self.assertEqual(1, PermissionForCollabDocument.objects.count())
        with self.assertRaises(IntegrityError):
            PermissionForCollabDocument.objects.create(**permission_data)
        self.assertEqual(1, PermissionForCollabDocument.objects.count())


class PermissionForCollabDocumentViewTest(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.url = "/api/collab/permission_for_collab_document/"

    def test_post_no_permission(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )

        to_post = {
            "group_has_permission": self.base_fixtures["groups"][0].id,
            "permission": permission.id,
            "document": document.id,
        }

        client: APIClient = self.base_fixtures["users"][0]["client"]
        response: Response = client.post(self.url, to_post)

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, PermissionForCollabDocument.objects.count())

    def test_post_with_permission(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        HasPermission.objects.create(
            permission=Permission.objects.get(
                name=PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC
            ),
            group_has_permission=self.base_fixtures["groups"][0],
            permission_for_rlc=self.base_fixtures["rlc"],
        )

        to_post = {
            "group_has_permission": self.base_fixtures["groups"][0].id,
            "permission": permission.id,
            "document": document.id,
        }

        client: APIClient = self.base_fixtures["users"][0]["client"]
        response: Response = client.post(self.url, to_post)

        self.assertEqual(201, response.status_code)
        self.assertEqual(1, PermissionForCollabDocument.objects.count())

    def test_post_wrong_document_id(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        HasPermission.objects.create(
            permission=Permission.objects.get(
                name=PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC
            ),
            group_has_permission=self.base_fixtures["groups"][0],
            permission_for_rlc=self.base_fixtures["rlc"],
        )

        to_post = {
            "group_has_permission": self.base_fixtures["groups"][0].id,
            "permission": permission.id,
            "document": document.id + 1,
        }

        client: APIClient = self.base_fixtures["users"][0]["client"]
        response: Response = client.post(self.url, to_post)

        self.assertEqual(400, response.status_code)
        self.assertEqual(0, PermissionForCollabDocument.objects.count())

    def test_delete_permission_blocked(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        permission_for_collab_document = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=permission,
            document=document,
        )
        self.assertEqual(1, PermissionForCollabDocument.objects.count())

        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/".format(self.url, permission_for_collab_document.id)
        response: Response = client.delete(url)

        self.assertEqual(403, response.status_code)
        self.assertEqual(1, PermissionForCollabDocument.objects.count())

    def test_delete_permission_success(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        permission_for_collab_document = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=permission,
            document=document,
        )
        self.assertEqual(1, PermissionForCollabDocument.objects.count())
        HasPermission.objects.create(
            permission=Permission.objects.get(
                name=PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC
            ),
            group_has_permission=self.base_fixtures["groups"][0],
            permission_for_rlc=self.base_fixtures["rlc"],
        )

        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/".format(self.url, permission_for_collab_document.id)
        response: Response = client.delete(url)

        self.assertEqual(204, response.status_code)
        self.assertEqual(0, PermissionForCollabDocument.objects.count())
