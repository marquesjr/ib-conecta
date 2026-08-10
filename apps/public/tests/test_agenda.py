from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from apps.public.models import EventIndexPage, EventPage


class AgendaPublicTests(TestCase):
    def setUp(self):
        self.root = Site.objects.get(is_default_site=True).root_page
        self.index = EventIndexPage(
            title="Agenda",
            slug="agenda",
            intro="Cultos e eventos da Igreja Batista em Santa Leopoldina.",
        )
        self.root.add_child(instance=self.index)
        self.index.save_revision().publish()
        self.starts = timezone.now() + timedelta(days=3)

    def test_published_future_event_appears_on_agenda_and_detail(self):
        event = EventPage(
            title="Culto de celebração",
            slug="culto-celebracao",
            starts_at=self.starts,
            location="Templo — Santa Leopoldina",
            body="<p>Venha adorar conosco.</p>",
            requires_registration=False,
        )
        self.index.add_child(instance=event)
        event.save_revision().publish()

        agenda = self.client.get("/agenda/")
        self.assertEqual(agenda.status_code, 200)
        self.assertContains(agenda, "Agenda")
        self.assertContains(agenda, "Culto de celebração")
        self.assertContains(agenda, "Templo — Santa Leopoldina")
        self.assertContains(agenda, "/agenda/culto-celebracao/")

        detail = self.client.get("/agenda/culto-celebracao/")
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Culto de celebração")
        self.assertContains(detail, "Templo — Santa Leopoldina")
        self.assertContains(detail, "Venha adorar conosco.")
        self.assertContains(detail, 'name="viewport"')

    def test_draft_event_is_hidden_from_agenda(self):
        event = EventPage(
            title="Ensaio interno",
            slug="ensaio-interno",
            starts_at=self.starts,
            location="Salão",
            body="<p>Somente equipe.</p>",
            requires_registration=False,
            live=False,
        )
        self.index.add_child(instance=event)
        event.save_revision()

        agenda = self.client.get("/agenda/")
        self.assertEqual(agenda.status_code, 200)
        self.assertNotContains(agenda, "Ensaio interno")
        self.assertEqual(self.client.get("/agenda/ensaio-interno/").status_code, 404)
