# Python program creating a
# context manager


def dangerous():
    raise Exception("dangerous function called")


class ContextManager:
    def __init__(self):

        print("init method called")

    def __enter__(self):
        print("enter method called")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("exit method called")
        print(exc_value, type(exc_value), str(exc_value))
        return True

    def do_sth(self):
        dangerous()
        print("do_sth method called")


with ContextManager() as manager:
    manager.do_sth()
    print("with statement block")
