from django.test import TestCase

from core.org.tests import example_data as ed


class ExampleDataTestCase(TestCase):
    def test_example_data_create_works(self):
        ed.create()
