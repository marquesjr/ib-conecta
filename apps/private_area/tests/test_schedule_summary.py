from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.private_area.models import AssignmentStatus, Ministry, MonthlySchedule, ScheduleAssignment

from .test_ministries import make_user


class ScheduleSummaryTests(TestCase):
    """Os totais do topo da escala contam só os próximos cultos (#105)."""

    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.ministry = Ministry.objects.create(name="Louvor")
        self.schedule = MonthlySchedule.objects.create(ministry=self.ministry, year=2026, month=9)
        now = timezone.now()
        self.future = now + timedelta(days=3)
        self.past = now - timedelta(days=3)

    def _assign(self, starts_at, function, status=AssignmentStatus.PENDING):
        return ScheduleAssignment.objects.create(
            schedule=self.schedule,
            starts_at=starts_at,
            function=function,
            participant=self.joao,
            status=status,
        )

    def _page(self):
        self.client.login(username="lider", password="senha-segura-123")
        return self.client.get(reverse("private_area:schedule_detail", args=[self.schedule.pk]))

    def test_counts_only_upcoming_services(self):
        self._assign(self.future, "Vocal")
        self._assign(self.future, "Teclado")
        self._assign(self.past, "Vocal", AssignmentStatus.CONFIRMED)
        self._assign(self.past, "Teclado", AssignmentStatus.CONFIRMED)
        self._assign(self.past, "Bateria", AssignmentStatus.DECLINED)
        page = self._page()
        self.assertEqual(page.context["summary_total"], 2)
        self.assertEqual(page.context["confirmed_count"], 0)
        self.assertEqual(page.context["pending_count"], 2)
        self.assertEqual(page.context["declined_count"], 0)
        self.assertContains(page, "Próximos cultos:")
        self.assertContains(page, "<strong>2</strong> convocações", html=False)
        self.assertNotContains(page, "recusada")

    def test_falls_back_to_past_services_when_none_upcoming(self):
        self._assign(self.past, "Vocal", AssignmentStatus.CONFIRMED)
        page = self._page()
        self.assertEqual(page.context["summary_total"], 1)
        self.assertEqual(page.context["confirmed_count"], 1)
        self.assertContains(page, "Cultos já realizados:")
        self.assertContains(page, "<strong>1</strong> convocação", html=False)
        self.assertContains(page, "<strong>1</strong> confirmada<", html=False)
