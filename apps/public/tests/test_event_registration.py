from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from apps.public.models import EventIndexPage, EventPage, EventRegistration


class EventRegistrationPublicTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        self.index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=self.index)
        self.index.save_revision().publish()

        self.open_event = EventPage(
            title="Retiro de jovens",
            slug="retiro-jovens",
            starts_at=timezone.now() + timedelta(days=10),
            location="Sítio da igreja",
            body="<p>Inscrições abertas.</p>",
            requires_registration=True,
        )
        self.index.add_child(instance=self.open_event)
        self.open_event.save_revision().publish()

        self.closed_event = EventPage(
            title="Culto sem inscrição",
            slug="culto-livre",
            starts_at=timezone.now() + timedelta(days=2),
            location="Templo",
            body="<p>Entrada livre.</p>",
            requires_registration=False,
        )
        self.index.add_child(instance=self.closed_event)
        self.closed_event.save_revision().publish()

    def test_public_can_register_for_event_that_requires_it(self):
        detail = self.client.get("/agenda/retiro-jovens/")
        self.assertContains(detail, "Inscrição")
        self.assertContains(detail, 'name="name"')
        self.assertContains(detail, 'name="email"')

        response = self.client.post(
            "/agenda/retiro-jovens/inscrever/",
            {
                "name": "Maria Silva",
                "email": "maria@example.com",
                "phone": "27999990000",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inscrição confirmada")
        self.assertContains(response, "Maria Silva")
        self.assertTrue(
            EventRegistration.objects.filter(
                event=self.open_event,
                email="maria@example.com",
                name="Maria Silva",
            ).exists()
        )

    def test_event_without_registration_has_no_form_and_rejects_post(self):
        detail = self.client.get("/agenda/culto-livre/")
        self.assertNotContains(detail, 'name="email"')
        self.assertNotContains(detail, "Confirmar inscrição")

        response = self.client.post(
            "/agenda/culto-livre/inscrever/",
            {
                "name": "João",
                "email": "joao@example.com",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(EventRegistration.objects.count(), 0)
