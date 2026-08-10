from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from apps.public.models import EventIndexPage, EventPage


class EventCalendarTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
        self.starts = timezone.now() + timedelta(days=7)
        self.event = EventPage(
            title="Batismo",
            slug="batismo",
            starts_at=self.starts,
            ends_at=self.starts + timedelta(hours=2),
            location="Rio Santa Maria",
            body="<p>Celebração de batismo.</p>",
            requires_registration=False,
        )
        index.add_child(instance=self.event)
        self.event.save_revision().publish()

    def test_event_detail_offers_ics_download(self):
        detail = self.client.get("/agenda/batismo/")
        self.assertContains(detail, "Adicionar ao calendário")
        self.assertContains(detail, "/agenda/batismo/calendario/")

        response = self.client.get("/agenda/batismo/calendario/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/calendar", response["Content-Type"])
        body = response.content.decode()
        self.assertIn("BEGIN:VCALENDAR", body)
        self.assertIn("BEGIN:VEVENT", body)
        self.assertIn("SUMMARY:Batismo", body)
        self.assertIn("LOCATION:Rio Santa Maria", body)
        self.assertIn("DTSTART;TZID=", body)
