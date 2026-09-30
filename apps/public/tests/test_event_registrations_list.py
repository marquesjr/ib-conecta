from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site

from apps.accounts.models import Role
from apps.public.models import EventIndexPage, EventPage, EventRegistration

User = get_user_model()


class EventRegistrationsListTests(TestCase):
    """Inscritos agrupados por evento, com filtro, contador e cancelar confirmado (#102)."""

    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
        self.retreat = self._event(index, "Retiro de famílias", "retiro", days=10)
        self.couples = self._event(index, "Encontro de casais", "casais", days=5)
        for name, status in [
            ("Igor Castro", EventRegistration.Status.CONFIRMED),
            ("Família Rocha", EventRegistration.Status.WAITLISTED),
            ("Bruno Dias", EventRegistration.Status.CANCELLED),
            ("Ana Lima", EventRegistration.Status.CONFIRMED),
        ]:
            EventRegistration.objects.create(
                event=self.retreat, name=name, email="a@example.com", status=status
            )
        self.ricardo = EventRegistration.objects.create(
            event=self.couples, name="Ricardo Alves", email="r@example.com"
        )
        user = User.objects.create_user(username="comissao", password="senha-segura-123")
        user.profile.role = Role.EVENTS_COMMISSION
        user.profile.save()
        self.client.login(username="comissao", password="senha-segura-123")
        self.url = reverse("accounts:event_registrations")

    def _event(self, index, title, slug, days):
        event = EventPage(
            title=title,
            slug=slug,
            starts_at=timezone.now() + timedelta(days=days),
            location="Templo",
            body="<p>Detalhes</p>",
            requires_registration=True,
        )
        index.add_child(instance=event)
        event.save_revision().publish()
        return event

    def test_groups_by_event_in_date_order_with_counts(self):
        response = self.client.get(self.url)
        html = response.content.decode()
        self.assertLess(html.index('id="registrations-event-%d"' % self.couples.pk),
                        html.index('id="registrations-event-%d"' % self.retreat.pk))
        groups = {g["event"].pk: g for g in response.context["groups"]}
        retreat = groups[self.retreat.pk]
        self.assertEqual(retreat["confirmed_count"], 2)
        self.assertEqual(retreat["waitlisted_count"], 1)
        self.assertEqual(retreat["cancelled_count"], 1)
        self.assertEqual(
            [r.name for r in retreat["registrations"]],
            ["Ana Lima", "Igor Castro", "Família Rocha", "Bruno Dias"],
        )
        self.assertContains(response, "<strong>2</strong> confirmadas", html=False)
        self.assertContains(response, "na lista de espera")

    def test_status_is_a_chip_not_trailing_text(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'class="state state--open"')
        self.assertContains(response, 'class="state state--closed"')
        self.assertNotContains(response, "· Confirmada")

    def test_filter_by_event(self):
        response = self.client.get(self.url, {"evento": self.couples.pk})
        self.assertContains(response, "Ricardo Alves")
        self.assertNotContains(response, "Igor Castro")
        self.assertContains(response, f'<option value="{self.couples.pk}" selected>')

    def test_unknown_filter_shows_all(self):
        response = self.client.get(self.url, {"evento": "abc"})
        self.assertContains(response, "Ricardo Alves")
        self.assertContains(response, "Igor Castro")

    def test_cancel_needs_a_second_step(self):
        response = self.client.get(self.url)
        self.assertContains(response, '<details class="registration-cancel">')
        self.assertContains(response, "Sim, cancelar inscrição")
        # Inscrição já cancelada não oferece cancelar de novo.
        self.assertEqual(response.content.decode().count("Sim, cancelar inscrição"), 4)

    def test_cancel_keeps_the_filter(self):
        cancel_url = reverse("accounts:event_registration_cancel", args=[self.ricardo.pk])
        response = self.client.post(cancel_url, {"evento": str(self.couples.pk)})
        self.assertRedirects(response, f"{self.url}?evento={self.couples.pk}")
        self.ricardo.refresh_from_db()
        self.assertEqual(self.ricardo.status, EventRegistration.Status.CANCELLED)
