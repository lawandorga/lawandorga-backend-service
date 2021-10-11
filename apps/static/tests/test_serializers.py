from django.test import SimpleTestCase

from apps.static.serializers import map_values


class TestCase(SimpleTestCase):
    def test_map_values(self):
        mapping = {
            "first": "a",
            "second": "b",
            "third": "x",
        }
        values = {"a": 123, "b": "letter", "c": "whatever"}
        expected = {"first": 123, "second": "letter"}
        result = map_values(mapping, values)
        for key, item in result.items():
            self.assertEqual(item, expected[key])
