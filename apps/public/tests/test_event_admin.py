from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site

from apps.accounts.models import Role
from apps.public.models import EventIndexPage, EventPage, EventRegistration

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class EventRegistrationAdminTests(TestCase):
    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page
        index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
        self.event = EventPage(
            title="Encontro de casais",
            slug="encontro-casais",
            starts_at=timezone.now() + timedelta(days=5),
            location="Templo",
            body="<p>Detalhes</p>",
            requires_registration=True,
        )
        index.add_child(instance=self.event)
        self.event.save_revision().publish()
        self.registration = EventRegistration.objects.create(
            event=self.event,
            name="Ana Costa",
            email="ana@example.com",
            phone="27988887777",
        )

    def test_events_commission_can_list_and_cancel_registration(self):
        make_user("comissao", Role.EVENTS_COMMISSION)
        self.client.login(username="comissao", password="senha-segura-123")

        list_url = reverse("accounts:event_registrations")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Costa")
        self.assertContains(response, "Encontro de casais")

        cancel_url = reverse(
            "accounts:event_registration_cancel",
            args=[self.registration.pk],
        )
        response = self.client.post(cancel_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, EventRegistration.Status.CANCELLED)
        self.assertContains(response, "Cancelada")

    def test_member_cannot_manage_registrations(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("accounts:event_registrations"))
        self.assertEqual(response.status_code, 403)
