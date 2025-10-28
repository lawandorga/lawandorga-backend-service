from uuid import uuid4

import pytest
from pydantic import ValidationError

from core.seedwork.use_case_layer import use_case
from core.seedwork.use_case_layer.injector import InjectionContext


class Actor:
    name = "Pete"


def test_actor_errors():
    @use_case()
    def f1():
        pass

    with pytest.raises(ValueError) as e:
        f1()

    assert "needs to have '__actor'" in str(e.value)

    @use_case()
    def f2(__actor):
        pass

    with pytest.raises(ValueError) as e:
        f2()

    assert "type hint to '__actor'" in str(e.value)

    @use_case()
    def f3(__actor: Actor):
        pass

    with pytest.raises(ValueError) as e:
        f3()

    assert "submit an '__actor'" in str(e.value)

    @use_case()
    def f4(__actor: Actor):
        pass

    with pytest.raises(TypeError) as e:
        f4({})

    assert "but should be" in str(e.value)

    @use_case()
    def f7(_=None, __actor: Actor = Actor()):
        pass

    with pytest.raises(ValueError) as e:
        f7()

    assert "submit an '__actor'" in str(e.value)

    @use_case()
    def f8(__actor: Actor, _):
        pass

    with pytest.raises(ValidationError):
        f8(0, __actor=Actor())


def test_actor_works():
    @use_case()
    def f5(__actor: Actor):
        pass

    f5(__actor=Actor())

    @use_case()
    def f6(_, __actor: Actor):
        pass

    f6(0, __actor=Actor())

    @use_case()
    def f7(_=None, __actor: Actor = Actor()):
        pass

    f7(__actor=Actor())


def test_findable():
    @use_case()
    def f1(__actor: Actor, x: int):
        assert x == 5

    f1(Actor(), 5)
    f1(__actor=Actor(), x=5)


def test_findable_errors():
    @use_case()
    def f1(__actor: Actor, x: str):
        assert x == "test"

    with pytest.raises(ValidationError):
        f1(Actor())

    with pytest.raises(ValidationError):
        f1(__actor=Actor())


class Repo:
    def get_key(self):
        return Key()


class Key:
    pass


def inject_key(r: Repo) -> Key:
    return r.get_key()


def test_injection_context():
    injections = InjectionContext(
        {
            Repo: Repo(),
            Key: inject_key,
        }
    )
    assert injections.has(Repo)
    assert injections.has(Key)


def test_use_case_with_unused_function_injection():
    def inject_key_not_called(r: Repo) -> Key:
        assert False

    injections = InjectionContext(
        {
            Repo: Repo(),
            Key: inject_key_not_called,
        }
    )

    @use_case(context=injections, callbacks=[])
    def t1(__actor: Actor):
        pass

    t1(__actor=Actor())


class Secret:
    pass


def get_secret(key: Key) -> Secret:
    assert isinstance(key, Key)
    return Secret()


def test_injections_injecting_themselfes():
    injections = InjectionContext(
        {
            Repo: Repo(),
            Key: inject_key,
            Secret: get_secret,
        }
    )

    @use_case(context=injections, callbacks=[])
    def t2(__actor: Actor, key: Key):
        assert isinstance(key, Key)

    t2(__actor=Actor())


class UniqueObject:
    def __init__(self) -> None:
        self.id = uuid4()


def test_callback_injection_is_same_as_usecase_injection():
    injections = InjectionContext(
        {
            UniqueObject: lambda: UniqueObject(),
        }
    )

    id = None

    def callback(unique_object: UniqueObject):
        nonlocal id
        assert id == unique_object.id

    @use_case(context=injections, callbacks=[callback])
    def t3(__actor: Actor, unique_object: UniqueObject):
        nonlocal id
        id = unique_object.id

    t3(__actor=Actor())


def test_callback_injection_different_from_usecase_injection():
    injections = InjectionContext(
        {
            UniqueObject: lambda: UniqueObject(),
        }
    )

    ids = set()

    @use_case(context=injections, callbacks=[])
    def t4(__actor: Actor, unique_object: UniqueObject):
        ids.add(unique_object.id)

    @use_case(context=injections, callbacks=[])
    def t5(__actor: Actor, unique_object: UniqueObject):
        ids.add(unique_object.id)

    t4(__actor=Actor())
    t5(__actor=Actor())
    assert len(ids) == 2
