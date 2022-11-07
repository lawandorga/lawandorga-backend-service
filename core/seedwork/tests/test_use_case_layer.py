import pytest

from core.seedwork.use_case_layer import find, use_case


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

    with pytest.raises(TypeError):
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
    def f1(__actor: Actor, x=find(lambda a, x: "test")):
        assert x == "test"

    f1(Actor(), 5)
    f1(__actor=Actor(), x=5)


def test_findable_errors():
    @use_case()
    def f1(__actor: Actor, x=find(lambda a, x: "test")):
        assert x == "test"

    with pytest.raises(ValueError):
        f1(Actor())

    with pytest.raises(ValueError):
        f1(__actor=Actor())
