from typing import Any


class CallbackContext:
    def __init__(self, success: bool, actor: Any, fn_name: str):
        self.success = success
        self.actor = actor
        self.fn_name = fn_name
