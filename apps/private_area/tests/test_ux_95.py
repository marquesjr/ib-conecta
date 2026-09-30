from django.test import TestCase
from django.urls import reverse

from apps.private_area.tests.test_ministries import ScheduleEditTests


class ScheduleMoreActionsTests(TestCase):
    """#95: no celular, só "Editar escala" fica à vista; o resto vai para "Mais ações"."""

    setUp = ScheduleEditTests.setUp

    def test_secondary_actions_grouped_under_more_actions(self):
        page = self.client.get(
            reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.assertContains(page, '<details class="more-actions">', html=False)
        self.assertContains(page, "Mais ações")
        self.assertContains(page, "Editar escala", count=1)
        # Cada ação secundária aparece na linha larga e no menu "Mais ações".
        self.assertContains(
            page, reverse("private_area:schedule_calendar", args=[self.schedule.pk]), count=2
        )
        self.assertContains(
            page, reverse("private_area:schedule_print", args=[self.schedule.pk]), count=2
        )
