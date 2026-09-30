from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from apps.public.event_facts import directions_url, when_label
from apps.public.models import EventIndexPage, EventPage, EventRegistration


def local(*args):
    return timezone.make_aware(datetime(*args))


class EventWhenLabelTests(TestCase):
    def test_same_day_shows_start_and_end_hours(self):
        self.assertEqual(
            when_label(local(2026, 10, 24, 17, 0), local(2026, 10, 24, 19, 30)),
            "Sábado, 24 de outubro de 2026 · 17h às 19h30",
        )

    def test_without_end_shows_start_only(self):
        self.assertEqual(
            when_label(local(2026, 10, 24, 9, 0)),
            "Sábado, 24 de outubro de 2026 · 9h",
        )

    def test_multi_day_names_both_days(self):
        self.assertEqual(
            when_label(local(2026, 10, 24, 17, 0), local(2026, 10, 26, 19, 0)),
            "Sábado, 24 de outubro de 2026, 17h, até segunda-feira, 26 de outubro de 2026, 19h",
        )

    def test_directions_url_encodes_location(self):
        self.assertEqual(
            directions_url("Rua A, 10 - Santa Leopoldina"),
            "https://www.google.com/maps/search/?api=1&query=Rua+A%2C+10+-+Santa+Leopoldina",
        )
        self.assertEqual(directions_url(""), "")


class EventFactsBlockTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        self.index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=self.index)
        self.index.save_revision().publish()

    def make_event(self, **fields):
        defaults = {
            "title": "Retiro de casais",
            "slug": "retiro",
            "starts_at": local(2026, 10, 24, 17, 0),
            "ends_at": local(2026, 10, 26, 19, 0),
            "location": "Sítio Boa Esperança",
        }
        defaults.update(fields)
        event = EventPage(**defaults)
        self.index.add_child(instance=event)
        event.save_revision().publish()
        return event

    def test_block_shows_when_where_and_directions(self):
        self.make_event()
        response = self.client.get("/agenda/retiro/")
        self.assertContains(response, 'class="event-facts"')
        self.assertContains(response, "<dt>Quando</dt>", html=True)
        self.assertContains(response, "Sábado, 24 de outubro de 2026, 17h")
        self.assertContains(response, "<dt>Onde</dt>", html=True)
        self.assertContains(response, "Sítio Boa Esperança")
        self.assertContains(response, "https://www.google.com/maps/search/?api=1&amp;query=S%C3%ADtio+Boa+Esperan%C3%A7a")
        self.assertContains(response, "Como chegar")
        self.assertContains(response, "/agenda/retiro/calendario/")
        self.assertNotContains(response, "<dt>Inscrição</dt>", html=True)

    def test_without_location_hides_where(self):
        self.make_event(location="")
        response = self.client.get("/agenda/retiro/")
        self.assertNotContains(response, "<dt>Onde</dt>", html=True)
        self.assertNotContains(response, "Como chegar")

    def test_registration_fact_links_to_form(self):
        self.make_event(requires_registration=True)
        response = self.client.get("/agenda/retiro/")
        self.assertContains(response, "<dt>Inscrição</dt>", html=True)
        self.assertContains(response, 'href="#inscricao"')
        self.assertContains(response, 'id="inscricao"')
        self.assertNotContains(response, "vaga")

    def test_retreat_shows_remaining_spots_and_waitlist(self):
        event = self.make_event(requires_registration=True, is_retreat=True, capacity=2)
        response = self.client.get("/agenda/retiro/")
        self.assertContains(response, "pagamento via PIX da igreja")
        self.assertContains(response, "2 vagas restantes.")

        for name in ("Ana", "Bia"):
            EventRegistration.objects.create(
                event=event, name=name, email=f"{name}@example.com",
                status=EventRegistration.Status.CONFIRMED,
            )
        response = self.client.get("/agenda/retiro/")
        self.assertContains(response, "Vagas esgotadas")
