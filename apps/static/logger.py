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
