from django.test import Client, TestCase
from django.utils import timezone

from core.events.models import EventsEvent
from core.events.use_cases.events import create_event, delete_event, update_event
from core.org.models import Meta, Org
from core.seedwork import test_helpers as data


class TestEvents(TestCase):
    def setUp(self):
        self.meta_org1 = Meta.objects.create(name="RLC Meta Org")
        self.meta_org2 = Meta.objects.create(name="Other Meta Org")
        self.rlc = Org.objects.create(name="Test RLC", meta=self.meta_org1)
        self.rlc2 = Org.objects.create(name="Second RLC", meta=self.meta_org1)
        self.other_org = Org.objects.create(name="Other Org", meta=self.meta_org2)
        self.user_1 = data.create_org_user(org=self.rlc)
        self.user_2 = data.create_org_user(email="dummy2@law-orga.de", org=self.rlc)

        self.event_1 = EventsEvent.objects.create(
            org=self.rlc,
            name="Test Event",
            description="",
            level="ORG",
            start_time=timezone.now(),
            end_time=timezone.now(),
        )
        self.event_2 = EventsEvent.objects.create(
            org=self.rlc2,
            name="Test Event 2",
            description="",
            level="META",
            start_time=timezone.now(),
            end_time=timezone.now(),
        )
        self.event_3 = EventsEvent.objects.create(
            org=self.rlc2,
            name="Test Event 3",
            description="",
            level="ORG",
            start_time=timezone.now(),
            end_time=timezone.now(),
        )
        self.event_of_other_meta_org = EventsEvent.objects.create(
            org=self.other_org,
            name="Test Event of other meta org",
            description="",
            level="META",
            start_time=timezone.now(),
            end_time=timezone.now(),
        )

        self.client = Client()
        self.client.login(**self.user_1)

    def test_get_events(self):
        res = self.client.get("/api/events/")

        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_create_event(self):
        event_data = {
            "name": "Test Event Create",
            "description": "",
            "level": "ORG",
            "start_time": timezone.now().isoformat(),
            "end_time": timezone.now().isoformat(),
        }
        create_event(self.user_1["org_user"], **event_data)

    def test_event_update(self):
        id = self.event_1.pk
        update_event(
            self.user_1["org_user"],
            id,
            description="Updated",
            name=self.event_1.name,
            start_time=self.event_1.start_time,
            end_time=self.event_1.end_time,
        )
        updated = EventsEvent.objects.get(id=id)
        assert updated.description == "Updated"

    def test_event_delete(self):
        id = self.event_1.pk
        delete_event(self.user_1["org_user"], id)
        all_events = EventsEvent.objects.all()
        assert len(all_events) == 3

    def test_ics_calendar(self):
        ics_cal = self.user_1["org_user"].get_ics_calendar()
        assert ics_cal.count("BEGIN:VEVENT") == 2
