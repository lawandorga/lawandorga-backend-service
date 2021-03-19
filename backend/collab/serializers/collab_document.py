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
from typing import Any

from rest_framework import serializers

from backend.collab.models import CollabDocument, UserProfile
from backend.static.permissions import (
    PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
    PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
    PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
)


class CollabDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabDocument
        fields = "__all__"


class CollabDocumentListSerializer(serializers.ModelSerializer):
    # TODO: doesn't work like that anymore
    children = serializers.SerializerMethodField()

    class Meta:
        model = CollabDocument
        fields = (
            "pk",
            "name",
            "created",
            "creator",
            "last_edited",
            "last_editor",
            "children",
        )

    def get_children(self, instance):
        children = instance.child_pages.all().order_by("name")
        return CollabDocumentListSerializer(children, many=True).data


class CollabDocumentPermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabDocument
        fields = "__all__"


class CollabDocumentTreeSerializer(serializers.ModelSerializer):
    child_pages = serializers.SerializerMethodField("get_sub_tree")

    def __init__(
        self,
        user: UserProfile,
        all_documents: [CollabDocument],
        overall_permission: bool,
        see_subfolders: bool,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user = user
        self.all_documents = all_documents
        self.overall_permission = overall_permission
        self.see_subfolders = see_subfolders

    class Meta:
        model = CollabDocument
        fields = (
            "pk",
            "path",
            "created",
            "creator",
            "last_edited",
            "last_editor",
            "child_pages",
        )

    def get_sub_tree(self, document: CollabDocument):
        child_documents = []
        for doc in self.all_documents:
            ancestor: bool = doc.path.startswith("{}/".format(document.path))
            direct_child: bool = "/" not in doc.path[len(document.path) + 1 :]

            if ancestor and direct_child:
                subfolders = False
                if self.overall_permission or self.see_subfolders:
                    add = True
                else:
                    add, subfolders = doc.user_can_see(self.user)
                if add:
                    child_documents.append(
                        CollabDocumentTreeSerializer(
                            instance=doc,
                            user=self.user,
                            all_documents=self.all_documents,
                            see_subfolders=subfolders or self.see_subfolders,
                            overall_permission=self.overall_permission,
                        ).data
                    )
        return child_documents
