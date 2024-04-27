from typing import Any, Callable, Iterable, Mapping, TypeVar


def to_list(obj):
    if isinstance(obj, list):
        return obj
    return list(obj)


group_by_I = TypeVar("group_by_I")
group_by_G = TypeVar("group_by_G")


def group_by(
    items: list[group_by_I], fn: Callable[[group_by_I], group_by_G]
) -> dict[group_by_G, list[group_by_I]]:
    grouped: dict[group_by_G, list[group_by_I]] = {}
    for item in items:
        key = fn(item)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped


set_default_K = TypeVar("set_default_K")
set_default_C = TypeVar("set_default_C")


def set_default(
    obj: dict[set_default_K, set_default_C],
    keys: Iterable[set_default_K],
    default: Callable[[], set_default_C],
) -> dict[set_default_K, set_default_C]:
    ret = obj.copy()
    for key in keys:
        if key not in ret:
            ret[key] = default()
    return ret


for_each_I = TypeVar("for_each_I")


def for_each(items: Iterable[for_each_I], fn: Callable[[for_each_I], Any | None]):
    for item in items:
        fn(item)


get_values_V = TypeVar("get_values_V")


def get_values(obj: Mapping[Any, get_values_V]) -> list[get_values_V]:
    return list(obj.values())


flatten_I = TypeVar("flatten_I")


def flatten(items: Iterable[Iterable[flatten_I]]) -> list[flatten_I]:
    return [item for sublist in items for item in sublist]


dict_map_K = TypeVar("dict_map_K")
dict_map_V = TypeVar("dict_map_V")
dict_map_R = TypeVar("dict_map_R")


def dict_map(
    obj: Mapping[dict_map_K, dict_map_V], fn: Callable[[dict_map_V], dict_map_R]
) -> dict[dict_map_K, dict_map_R]:
    return {k: fn(v) for k, v in obj.items()}


list_map_I = TypeVar("list_map_I")
list_map_O = TypeVar("list_map_O")


def list_map(
    items: Iterable[list_map_I], fn: Callable[[list_map_I], list_map_O]
) -> list[list_map_O]:
    return list(map(fn, items))


list_filter_I = TypeVar("list_filter_I")


def list_filter(
    items: Iterable[list_filter_I], fn: Callable[[list_filter_I], bool]
) -> list[list_filter_I]:
    return list(filter(fn, items))


take_single_I = TypeVar("take_single_I")


def take_single(items: list[take_single_I], pos: int) -> take_single_I | None:
    if len(items) > pos:
        return items[pos]
    return None


list_reduce_I = TypeVar("list_reduce_I")
list_reduce_R = TypeVar("list_reduce_R")


def list_reduce(
    items: Iterable[list_reduce_I],
    fn: Callable[[list_reduce_R, list_reduce_I], list_reduce_R],
    initial: list_reduce_R,
) -> list_reduce_R:
    ret = initial
    for item in items:
        ret = fn(ret, item)
    return ret


create_chunks_I = TypeVar("create_chunks_I")


def create_chunks(items: list[create_chunks_I], n) -> Iterable[list[create_chunks_I]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(items), n):
        yield items[i : i + n]
