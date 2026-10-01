from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.private_area.models import AssignmentStatus, Ministry, MonthlySchedule, ScheduleAssignment

User = get_user_model()


class AwaitingAnswerOnHomeTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(username="membro", password="senha-segura-123")
        self.member.profile.role = Role.MEMBER
        self.member.profile.save()
        ministry = Ministry.objects.create(name="Louvor")
        self.schedule = MonthlySchedule.objects.create(ministry=ministry, year=2026, month=9)
        self.client.login(username="membro", password="senha-segura-123")

    def _assign(self, starts_at, function, status=AssignmentStatus.PENDING):
        return ScheduleAssignment.objects.create(
            schedule=self.schedule,
            starts_at=starts_at,
            function=function,
            participant=self.member,
            status=status,
        )

    def test_pending_future_assignment_shows_answer_buttons(self):
        assignment = self._assign(timezone.now() + timedelta(days=2), "Violão")
        response = self.client.get(reverse("private_area:home"))
        self.assertContains(response, "Precisa da sua resposta")
        self.assertContains(
            response,
            f'action="{reverse("private_area:assignment_respond", args=[assignment.pk])}"',
        )
        self.assertContains(response, 'value="confirm"')
        self.assertContains(response, 'value="decline"')

    def test_block_is_hidden_without_pending_future_assignments(self):
        self._assign(timezone.now() + timedelta(days=2), "Teclado", AssignmentStatus.CONFIRMED)
        self._assign(timezone.now() - timedelta(days=2), "Bateria")
        response = self.client.get(reverse("private_area:home"))
        self.assertNotContains(response, "Precisa da sua resposta")
        self.assertContains(response, "Minhas convocações")

    def test_confirming_from_home_returns_to_home(self):
        assignment = self._assign(timezone.now() + timedelta(days=2), "Violão")
        home = reverse("private_area:home")
        response = self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "confirm", "next": home},
        )
        self.assertRedirects(response, home)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.CONFIRMED)
        self.assertNotContains(self.client.get(home), "Precisa da sua resposta")

    def test_declining_from_home_returns_to_home(self):
        assignment = self._assign(timezone.now() + timedelta(days=2), "Violão")
        home = reverse("private_area:home")
        response = self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "decline", "next": home},
        )
        self.assertRedirects(response, home)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.DECLINED)

    def test_external_next_is_ignored(self):
        assignment = self._assign(timezone.now() + timedelta(days=2), "Violão")
        response = self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "confirm", "next": "https://example.com/"},
        )
        self.assertRedirects(
            response, reverse("private_area:assignment_respond", args=[assignment.pk])
        )

    def test_date_and_chip_are_separate_elements(self):
        self._assign(timezone.now() + timedelta(days=2), "Violão")
        response = self.client.get(reverse("private_area:home"))
        self.assertRegex(response.content.decode(), r"\d{1,2}h(?:\d{2})?</span>\s*<span class=\"state")
