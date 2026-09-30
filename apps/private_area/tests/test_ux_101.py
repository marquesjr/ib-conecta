from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.private_area.models import EventOperation
from apps.private_area.tests.test_event_operations import make_user, publish_event


def operate(event):
    return EventOperation.objects.create(public_event=event)


class EventCalendarNavigationTests(TestCase):
    def setUp(self):
        make_user("comissao", Role.EVENTS_COMMISSION)
        self.client.login(username="comissao", password="senha-segura-123")
        self.url = reverse("private_area:event_calendar")

    def test_year_selector_has_previous_and_next_arrows(self):
        response = self.client.get(self.url, {"year": 2030})
        self.assertContains(response, 'class="year-nav"')
        self.assertContains(response, f'href="{self.url}?year=2029"')
        self.assertContains(response, f'href="{self.url}?year=2031"')
        self.assertContains(response, 'aria-label="Ano anterior, 2029"')
        self.assertContains(response, 'aria-label="Próximo ano, 2031"')
        self.assertContains(response, '<strong class="year-nav-current" aria-current="page">2030</strong>', html=True)

    def test_add_button_replaces_operar_evento_label(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Adicionar evento")
        self.assertContains(response, reverse("private_area:event_operation_create"))
        self.assertNotContains(response, ">Operar evento<")

    def test_operations_are_grouped_by_month(self):
        tz = timezone.get_current_timezone()
        march = publish_event(title="Encontro de março", slug="marco")
        march.starts_at = datetime(2030, 3, 10, 19, 0, tzinfo=tz)
        march.save()
        march_two = publish_event(title="Culto de março", slug="marco-2")
        march_two.starts_at = datetime(2030, 3, 24, 19, 0, tzinfo=tz)
        march_two.save()
        july = publish_event(title="Retiro de julho", slug="julho")
        july.starts_at = datetime(2030, 7, 5, 8, 0, tzinfo=tz)
        july.save()
        for event in (march, march_two, july):
            operate(event)
        response = self.client.get(self.url, {"year": 2030})
        content = response.content.decode()
        self.assertEqual(content.count('class="section-label calendar-month"'), 2)
        self.assertContains(response, "Março")
        self.assertContains(response, "Julho")
        self.assertLess(content.index("Março"), content.index("Encontro de março"))
        self.assertLess(content.index("Culto de março"), content.index("Julho"))
        self.assertLess(content.index("Julho"), content.index("Retiro de julho"))


class EventCalendarFinanceViewTests(TestCase):
    def test_finance_role_does_not_see_add_button(self):
        make_user("tesoureiro", Role.TREASURY)
        self.client.login(username="tesoureiro", password="senha-segura-123")
        response = self.client.get(reverse("private_area:event_calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Adicionar evento")
