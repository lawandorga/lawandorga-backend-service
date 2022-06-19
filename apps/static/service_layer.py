class ServiceResult:
    def __init__(self, message: str, data=None, error=None):
        self.message = message
        if data:
            self.success = True
            self.data = data
        elif error:
            self.success = False
            self.error = error
        else:
            self.data = {}
            self.success = True

    @property
    def value(self):
        if self.success:
            return self.data
        else:
            return self.error
