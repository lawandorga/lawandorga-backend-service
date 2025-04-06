from functools import partial, wraps
from typing import Callable, ClassVar, TypeVar
from uuid import uuid4

from messagebus.domain.collector import EventCollector
from messagebus.domain.event import Event

RetType = TypeVar("RetType")


def inject_collector(func: Callable[..., RetType]) -> Callable[..., RetType]:
    collector = EventCollector()
    injected_func = partial(func, collector=collector)
    setattr(injected_func, "collector", collector)

    @wraps(injected_func)
    def wrapper(*args, **kwargs) -> RetType:
        return injected_func(*args, **kwargs)

    return wrapper


class Agg:
    class NumbersAdded(Event):
        a: int
        b: int
        result: int
        action: ClassVar[str] = "numbers_added"

        def get_str(self) -> str:
            return f"Added {self.a} and {self.b}, result is {self.result}"


@inject_collector
def plus(a: int, b: int, collector: EventCollector) -> int:
    result = a + b
    collector.collect(Agg.NumbersAdded(a=a, b=b, result=result, uuid=uuid4()))
    return result


def test_events_are_added():
    result = plus(1, 2)
    assert result == 3
    collector = getattr(plus, "collector")
    assert collector.pop().get_str() == "Added 1 and 2, result is 3"


def test_events_are_added_with_multiple_calls():
    plus(1, 2)
    collector = getattr(plus, "collector")
    assert collector.pop().get_str() == "Added 1 and 2, result is 3"
    plus(3, 4)
    assert collector.pop().get_str() == "Added 3 and 4, result is 7"
    assert collector.pop() is None
