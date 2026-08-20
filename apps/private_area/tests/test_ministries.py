from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import AuditLog, Role
from apps.private_area.models import AssignmentStatus, Ministry, MonthlySchedule, ScheduleAssignment

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


class MinistryAccessTests(TestCase):
    def test_visitor_is_redirected_from_ministry_list(self):
        response = self.client.get(reverse("private_area:ministry_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_member_can_list_ministries_but_cannot_create(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        listing = self.client.get(reverse("private_area:ministry_list"))
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, "Ministérios")
        create = self.client.get(reverse("private_area:ministry_create"))
        self.assertEqual(create.status_code, 403)
        denied = self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": "Ministério de louvor"},
        )
        self.assertEqual(denied.status_code, 403)

    def test_leader_can_create_a_ministry(self):
        make_user("lider", Role.MINISTRY_LEADER)
        self.client.login(username="lider", password="senha-segura-123")
        page = self.client.get(reverse("private_area:ministry_create"))
        self.assertEqual(page.status_code, 200)
        response = self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": "Cânticos e instrumentos"},
        )
        self.assertEqual(response.status_code, 302)
        listing = self.client.get(reverse("private_area:ministry_list"))
        self.assertContains(listing, "Louvor")
        detail = self.client.get(response.url)
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Louvor")
        self.assertContains(detail, "Cânticos e instrumentos")


class MonthlyScheduleTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.maria = make_user("maria", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        created = self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": ""},
        )
        self.ministry = Ministry.objects.get(name="Louvor")
        self.assertEqual(created.status_code, 302)

    def test_member_cannot_create_a_schedule(self):
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 9, "notes": ""},
        )
        self.assertEqual(response.status_code, 403)

    def test_leader_builds_monthly_schedule_with_participant_and_function(self):
        created = self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 9, "notes": "Cultos de setembro"},
        )
        self.assertEqual(created.status_code, 302)
        page = self.client.get(created.url)
        self.assertContains(page, "setembro")
        self.assertContains(page, "2026")
        added = self.client.post(
            reverse(
                "private_area:assignment_add",
                args=[MonthlySchedule.objects.get().pk],
            ),
            {
                "starts_at": "2026-09-06T19:00",
                "function": "Vocal",
                "participant": self.joao.pk,
            },
        )
        self.assertEqual(added.status_code, 302)
        schedule = self.client.get(created.url)
        self.assertContains(schedule, "Vocal")
        self.assertContains(schedule, "joao")

    def test_participant_can_confirm_assignment(self):
        assignment = self._add_assignment(self.joao, "Vocal")
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        page = self.client.get(
            reverse("private_area:assignment_respond", args=[assignment.pk])
        )
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Confirmar")
        self.assertContains(page, "Recusar")
        response = self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "confirm"},
        )
        self.assertEqual(response.status_code, 302)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.CONFIRMED)

    def test_participant_can_decline_assignment(self):
        assignment = self._add_assignment(self.joao, "Dirigente")
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "decline"},
        )
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.DECLINED)

    def test_other_member_cannot_respond_to_someone_elses_assignment(self):
        assignment = self._add_assignment(self.joao, "Vocal")
        self.client.logout()
        self.client.login(username="maria", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:assignment_respond", args=[assignment.pk]),
            {"action": "confirm"},
        )
        self.assertEqual(response.status_code, 403)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.PENDING)

    def test_leader_records_a_substitution(self):
        assignment = self._add_assignment(self.joao, "Vocal")
        response = self.client.post(
            reverse("private_area:assignment_substitute", args=[assignment.pk]),
            {"substitute": self.maria.pk},
        )
        self.assertEqual(response.status_code, 302)
        assignment.refresh_from_db()
        self.assertEqual(assignment.participant_id, self.maria.pk)
        self.assertEqual(assignment.status, AssignmentStatus.PENDING)
        page = self.client.get(
            reverse("private_area:schedule_detail", args=[assignment.schedule_id])
        )
        self.assertContains(page, "maria")
        self.assertContains(page, "joao")
        self.assertContains(page, "Substituição")
        entry = AuditLog.objects.filter(action="assignment_substituted").latest("created_at")
        self.assertEqual(entry.metadata.get("replaced_user_id"), self.joao.pk)
        self.assertEqual(entry.metadata.get("substitute_user_id"), self.maria.pk)

    def _add_assignment(self, participant, function: str) -> ScheduleAssignment:
        created = self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 9, "notes": ""},
        )
        self.assertEqual(created.status_code, 302)
        schedule = MonthlySchedule.objects.get()
        added = self.client.post(
            reverse("private_area:assignment_add", args=[schedule.pk]),
            {
                "starts_at": "2026-09-06T19:00",
                "function": function,
                "participant": participant.pk,
            },
        )
        self.assertEqual(added.status_code, 302)
        return ScheduleAssignment.objects.get()


class ScheduleExportTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": ""},
        )
        ministry = Ministry.objects.get()
        self.client.post(
            reverse("private_area:schedule_create", args=[ministry.pk]),
            {"year": 2026, "month": 9, "notes": ""},
        )
        self.schedule = MonthlySchedule.objects.get()
        self.client.post(
            reverse("private_area:assignment_add", args=[self.schedule.pk]),
            {
                "starts_at": "2026-09-06T19:00",
                "function": "Vocal",
                "participant": self.joao.pk,
            },
        )

    def test_visitor_cannot_export_the_schedule(self):
        self.client.logout()
        calendar = self.client.get(
            reverse("private_area:schedule_calendar", args=[self.schedule.pk])
        )
        self.assertEqual(calendar.status_code, 302)
        self.assertIn(reverse("accounts:login"), calendar.url)
        printable = self.client.get(
            reverse("private_area:schedule_print", args=[self.schedule.pk])
        )
        self.assertEqual(printable.status_code, 302)
        self.assertIn(reverse("accounts:login"), printable.url)

    def test_member_can_download_schedule_as_calendar(self):
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        response = self.client.get(
            reverse("private_area:schedule_calendar", args=[self.schedule.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/calendar", response["Content-Type"])
        body = response.content.decode()
        self.assertIn("BEGIN:VCALENDAR", body)
        self.assertIn("BEGIN:VEVENT", body)
        self.assertIn("SUMMARY:Louvor — Vocal", body)

    def test_print_page_lists_assignments_for_saving_pdf(self):
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        response = self.client.get(
            reverse("private_area:schedule_print", args=[self.schedule.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Salvar como PDF")
        self.assertContains(response, "Vocal")
        self.assertContains(response, "joao")
        self.assertContains(response, "Louvor")

    def test_authenticated_member_can_share_schedule_via_whatsapp(self):
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        page = self.client.get(
            reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "wa.me")
        self.assertContains(page, "Compartilhar no WhatsApp")
