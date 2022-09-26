class ServiceResult:
    def __init__(self, message: str, data=None, error=None):
        self._message = message
        if data is not None:
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

    @property
    def message(self):
        if self.success:
            return "SUCCESS: {}".format(self._message)
        else:
            return "ERROR: {}".format(self._message)
