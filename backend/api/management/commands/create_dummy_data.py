#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from django.core.management.base import BaseCommand
from .commands import (
    reset_db,
    create_dummy_data,
)


class Command(BaseCommand):
    help = "Populates database for deployment environment."

    def handle(self, *args, **options):
        # reset
        reset_db()
        create_dummy_data()
        # populate_deploy_db()

        # # create the dummy rlc
        # rlc = ed.create_rlc()
        #
        # # create users
        # users = ed.create_users(rlc)
        #
        # # create the dummy user you can login with to test everything
        # dummy_users = ed.create_dummy_users(rlc)
        # main_user = dummy_users[0]
        # users = dummy_users + users
        #
        # # create inactive user
        # mr_inactive = ed.create_inactive_user(rlc)
        #
        # # create groups
        # groups = ed.create_groups(rlc, main_user, users)
        # admin_group = ed.create_admin_group(rlc, main_user)
        #
        # # create clients
        # clients = ed.create_clients(rlc)
        #
        # # create records
        # records = ed.create_records(clients, users, rlc)
        # # TODO: create best record
        # best_record = self.create_the_best_record_ever(main_user, clients, users, rlc)
        #
        # # TODO: create requests
        # self.create_record_deletion_request(main_user, best_record)
        # self.create_record_permission_request(users[4], best_record)
        #
        # # TODO: delete later
        # migrate_to_encryption()
        # migrate_to_rlc_settings()
        #
        # # TODO: create notifications
        # best_encrypted_record = record_models.EncryptedRecord.objects.filter(
        #     record_token=best_record.record_token
        # ).first()
        # groups_list = list(api_models.Group.objects.all())
        # groups = [groups_list[0], groups_list[1]]
        # Command.create_notifications(
        #     main_user, dummy_users[-1], best_encrypted_record, groups
        # )
