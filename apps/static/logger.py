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

import logging


class Logger:
    @staticmethod
    def get_logger() -> logging.Logger:
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def debug(msg: str):
        Logger.get_logger().debug(msg)

    @staticmethod
    def error(msg: str):
        Logger.get_logger().error(msg)

    @staticmethod
    def info(msg: str):
        Logger.get_logger().info(msg)
