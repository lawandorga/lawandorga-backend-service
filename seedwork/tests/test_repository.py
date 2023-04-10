from seedwork.repository import SingletonRepository


class InterfaceRepo(SingletonRepository):
    SETTING = "TEST"
    IN_MEMORY = True

    @classmethod
    def get_module(cls):
        if cls.IN_MEMORY:
            return InMemoryRepo
        return StupidRepo

    def save(self, obj):
        raise NotImplementedError()


class InMemoryRepo(InterfaceRepo):
    def save(self, obj):
        self._obj = obj


class StupidRepo(InterfaceRepo):
    def save(self, _):
        self._obj = None


def test_singleton():
    repo1 = InMemoryRepo()
    repo2 = InMemoryRepo()
    assert repo1 == repo2


def test_repo_select():
    repo = InterfaceRepo()
    assert isinstance(repo, InMemoryRepo)


def test_repo_switch():
    repo1 = InterfaceRepo()
    assert isinstance(repo1, InMemoryRepo)
    InterfaceRepo.IN_MEMORY = False
    repo2 = InterfaceRepo()
    assert isinstance(repo2, StupidRepo)
