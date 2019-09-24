#  rlcapp - record and organization management software for refugee law clinics
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

import os
from backend.static.error_codes import ERROR__ENV__MISSING_VARIABLE
from backend.api.errors import CustomError


def get_website_base_url():
    return get_env_variable('URL')


def get_env_variable(variable_name):
    if variable_name not in os.environ:
        raise CustomError(ERROR__ENV__MISSING_VARIABLE)
    return os.environ[variable_name]
