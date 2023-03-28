from core.records.helpers import merge_attrs


def test_merge_attrs():
    attrs1 = {"a": 1, "b": 2}
    attrs2 = {"c": 3, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {"a": 1, "b": 2, "c": 3, "d": 4}


def test_merge_attrs_to_list():
    attrs1 = {"a": 1, "b": 2}
    attrs2 = {"a": 3, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {"a": [1, 3], "b": 2, "d": 4}


def test_merge_attrs_to_list_deep():
    attrs1 = {"a": 1, "b": ["a", "b", {"c": 1}]}
    attrs2 = {"a": 3, "b": 4, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {
        "a": [1, 3],
        "b": ["a", "b", {"c": 1}, 4],
        "d": 4,
    }


def test_merge_attrs_list():
    attrs1 = {"a": 1, "b": ["a", "b"]}
    attrs2 = {"a": 3, "b": 4, "d": 4}
    assert merge_attrs(attrs1, attrs2) == {
        "a": [1, 3],
        "b": ["a", "b", 4],
        "d": 4,
    }


def test_merge_attrs_list_reverse():
    attrs2 = {"a": 3, "b": 4, "d": 4}
    attrs1 = {"a": 1, "b": ["a", "b"]}
    assert merge_attrs(attrs2, attrs1) == {
        "a": [3, 1],
        "b": [4, "a", "b"],
        "d": 4,
    }
