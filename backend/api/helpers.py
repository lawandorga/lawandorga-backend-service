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



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def resolve_missing_rlc_keys_entries(user, users_private_key):
    from backend.api.models import MissingRlcKey, UsersRlcKeys
    from backend.static.encryption import RSAEncryption
    # a = list(MissingRlcKey.objects.filter(user=user))
    # if MissingRlcKey.objects.filter(user=user).exists():
    #     return

    missing_rlc_keys = MissingRlcKey.objects.filter(user__rlc=user.rlc)
    # rlcs_private_key = user.get_rlcs_private_key(users_private_key)
    rlcs_aes_key = user.get_rlcs_aes_key(users_private_key)
    for missing_rlc_key in missing_rlc_keys:
        # encrypt for user
        missing_rlc_key.user.generate_rlc_keys_for_this_user(rlcs_aes_key)
        missing_rlc_key.user.is_active = True
        missing_rlc_key.user.save()
        missing_rlc_key.delete()
