from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.private_area.models import Ministry, MonthlySchedule, ScheduleAssignment

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class RosterActionButtonsTests(TestCase):
    """#96: ações de cada pessoa na escala são botões com área de toque de 44 px."""

    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.joao.first_name, self.joao.last_name = "João", "Pereira"
        self.joao.save()
        schedule = MonthlySchedule.objects.create(
            ministry=Ministry.objects.create(name="Louvor"), year=2026, month=10
        )
        self.assignment = ScheduleAssignment.objects.create(
            schedule=schedule,
            starts_at=timezone.now() + timedelta(days=3),
            function="Vocal",
            participant=self.joao,
        )
        self.url = reverse("private_area:schedule_detail", args=[schedule.pk])

    def test_leader_actions_are_buttons_named_after_the_person(self):
        self.client.login(username="lider", password="senha-segura-123")
        page = self.client.get(self.url)
        edit = reverse("private_area:assignment_edit", args=[self.assignment.pk])
        substitute = reverse("private_area:assignment_substitute", args=[self.assignment.pk])
        self.assertContains(
            page,
            f'<a class="roster-action" href="{edit}" aria-label="Editar convocação de João Pereira">Editar</a>',
            html=True,
        )
        self.assertContains(
            page,
            f'<a class="roster-action" href="{substitute}" aria-label="Substituir João Pereira">Substituir</a>',
            html=True,
        )

    def test_participant_respond_link_is_a_button(self):
        self.client.login(username="joao", password="senha-segura-123")
        page = self.client.get(self.url)
        respond = reverse("private_area:assignment_respond", args=[self.assignment.pk])
        self.assertContains(
            page, f'<a class="roster-action" href="{respond}">Responder</a>', html=True
        )

    def test_roster_action_has_44px_touch_target(self):
        css = (Path(settings.BASE_DIR) / "static/css/ib-conecta.css").read_text()
        rule = css.split(".roster-action {", 1)[1].split("}", 1)[0]
        self.assertIn("min-height: 44px", rule)
