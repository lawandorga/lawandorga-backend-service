class UseCaseError(Exception):
    def __init__(self, message):
        self.message = message


class UseCaseInputError(Exception):
    def __init__(self, param_errors: dict[str, list[str]] | None = None):
        self.message = "Input Error"
        self.param_errors = param_errors
