from apps.api.tests import example_data as ed
from django.test import TestCase


class ExampleDataTestCase(TestCase):
    def test_example_data_create_works(self):
        ed.create()
