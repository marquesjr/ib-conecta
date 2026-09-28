from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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


class ScheduleEditTests(TestCase):
    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.maria = make_user("maria", Role.MEMBER)
        self.client.login(username="lider", password="senha-segura-123")
        self.client.post(
            reverse("private_area:ministry_create"),
            {"name": "Louvor", "description": ""},
        )
        self.ministry = Ministry.objects.get()
        self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 10, "notes": "Ensaio geral"},
        )
        self.schedule = MonthlySchedule.objects.get()
        self.client.post(
            reverse("private_area:assignment_add", args=[self.schedule.pk]),
            {
                "starts_at": "2026-10-03T19:00",
                "function": "Vocal",
                "participant": self.joao.pk,
            },
        )
        self.assignment = ScheduleAssignment.objects.get()

    def test_leader_sees_edit_links_on_schedule(self):
        page = self.client.get(
            reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.assertContains(page, reverse("private_area:schedule_edit", args=[self.schedule.pk]))
        self.assertContains(
            page, reverse("private_area:assignment_edit", args=[self.assignment.pk])
        )

    def test_member_cannot_edit_schedule_or_assignment(self):
        self.client.logout()
        self.client.login(username="joao", password="senha-segura-123")
        page = self.client.get(
            reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.assertNotContains(page, "Editar escala")
        for url in (
            reverse("private_area:schedule_edit", args=[self.schedule.pk]),
            reverse("private_area:assignment_edit", args=[self.assignment.pk]),
            reverse("private_area:assignment_remove", args=[self.assignment.pk]),
        ):
            self.assertEqual(self.client.post(url, {}).status_code, 403)
        self.assertTrue(ScheduleAssignment.objects.filter(pk=self.assignment.pk).exists())

    def test_leader_edits_schedule_notes_and_month(self):
        form = self.client.get(reverse("private_area:schedule_edit", args=[self.schedule.pk]))
        self.assertEqual(form.status_code, 200)
        self.assertContains(form, "Ensaio geral")
        response = self.client.post(
            reverse("private_area:schedule_edit", args=[self.schedule.pk]),
            {"year": 2026, "month": 11, "notes": "Ensaio na quinta"},
        )
        self.assertRedirects(
            response, reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.month, 11)
        self.assertEqual(self.schedule.notes, "Ensaio na quinta")
        self.assertEqual(self.schedule.ministry_id, self.ministry.pk)
        self.assertTrue(AuditLog.objects.filter(action="schedule_updated").exists())

    def test_edit_rejects_month_already_taken(self):
        self.client.post(
            reverse("private_area:schedule_create", args=[self.ministry.pk]),
            {"year": 2026, "month": 11, "notes": ""},
        )
        response = self.client.post(
            reverse("private_area:schedule_edit", args=[self.schedule.pk]),
            {"year": 2026, "month": 11, "notes": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Já existe uma escala para este mês.")
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.month, 10)

    def test_edit_form_shows_current_assignment_values(self):
        page = self.client.get(
            reverse("private_area:assignment_edit", args=[self.assignment.pk])
        )
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'value="2026-10-03T19:00"')
        self.assertContains(page, 'value="Vocal"')

    def test_changing_function_keeps_confirmation(self):
        self.assignment.status = AssignmentStatus.CONFIRMED
        self.assignment.save()
        self.client.post(
            reverse("private_area:assignment_edit", args=[self.assignment.pk]),
            {
                "starts_at": "2026-10-03T19:00",
                "function": "Dirigente",
                "participant": self.joao.pk,
            },
        )
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.function, "Dirigente")
        self.assertEqual(self.assignment.status, AssignmentStatus.CONFIRMED)

    def test_changing_date_or_person_resets_confirmation(self):
        self.assignment.status = AssignmentStatus.CONFIRMED
        self.assignment.save()
        response = self.client.post(
            reverse("private_area:assignment_edit", args=[self.assignment.pk]),
            {
                "starts_at": "2026-10-10T18:30",
                "function": "Vocal",
                "participant": self.maria.pk,
            },
        )
        self.assertRedirects(
            response, reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.participant_id, self.maria.pk)
        self.assertEqual(self.assignment.status, AssignmentStatus.PENDING)
        entry = AuditLog.objects.filter(action="assignment_updated").latest("created_at")
        self.assertIn("participant", entry.metadata["changed"])
        self.assertIn("starts_at", entry.metadata["changed"])

    def test_leader_removes_assignment(self):
        self.assertEqual(
            self.client.get(
                reverse("private_area:assignment_remove", args=[self.assignment.pk])
            ).status_code,
            405,
        )
        response = self.client.post(
            reverse("private_area:assignment_remove", args=[self.assignment.pk])
        )
        self.assertRedirects(
            response, reverse("private_area:schedule_detail", args=[self.schedule.pk])
        )
        self.assertFalse(ScheduleAssignment.objects.exists())
        self.assertTrue(AuditLog.objects.filter(action="assignment_removed").exists())


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


class ScheduleLayoutTests(TestCase):
    """A escala agrupa convocações por culto e mostra ações só onde cabem."""

    def setUp(self):
        self.leader = make_user("lider", Role.MINISTRY_LEADER)
        self.joao = make_user("joao", Role.MEMBER)
        self.joao.first_name, self.joao.last_name = "João", "Pereira"
        self.joao.save()
        self.ministry = Ministry.objects.create(name="Louvor")
        self.schedule = MonthlySchedule.objects.create(ministry=self.ministry, year=2026, month=9)
        now = timezone.now()
        self.future = now + timedelta(days=3)
        self.past = now - timedelta(days=3)

    def _assign(self, starts_at, function, participant, status=AssignmentStatus.PENDING):
        return ScheduleAssignment.objects.create(
            schedule=self.schedule,
            starts_at=starts_at,
            function=function,
            participant=participant,
            status=status,
        )

    def _page(self, username):
        self.client.login(username=username, password="senha-segura-123")
        return self.client.get(reverse("private_area:schedule_detail", args=[self.schedule.pk]))

    def test_shows_full_name_instead_of_login(self):
        self._assign(self.future, "Vocal", self.joao)
        page = self._page("lider")
        self.assertContains(page, "João Pereira")

    def test_groups_assignments_by_service(self):
        self._assign(self.future, "Vocal", self.joao)
        self._assign(self.future, "Projeção", self.leader)
        self._assign(self.past, "Vocal", self.joao, AssignmentStatus.CONFIRMED)
        page = self._page("lider")
        self.assertEqual(len(page.context["upcoming_services"]), 1)
        self.assertEqual(len(page.context["upcoming_services"][0].assignments), 2)
        self.assertEqual(len(page.context["past_services"]), 1)
        self.assertContains(page, "1 culto já realizado")

    def test_respond_link_only_for_own_pending_future_assignment(self):
        pending = self._assign(self.future, "Vocal", self.joao)
        confirmed = self._assign(self.future, "Dirigente", self.joao, AssignmentStatus.CONFIRMED)
        past = self._assign(self.past, "Vocal", self.joao)
        page = self._page("joao")
        self.assertContains(page, reverse("private_area:assignment_respond", args=[pending.pk]))
        self.assertNotContains(page, reverse("private_area:assignment_respond", args=[confirmed.pk]))
        self.assertNotContains(page, reverse("private_area:assignment_respond", args=[past.pk]))
        self.assertContains(page, "Sua convocação:")

    def test_substitution_link_hidden_for_past_services(self):
        future = self._assign(self.future, "Vocal", self.joao)
        past = self._assign(self.past, "Vocal", self.joao)
        page = self._page("lider")
        self.assertContains(page, reverse("private_area:assignment_substitute", args=[future.pk]))
        self.assertNotContains(page, reverse("private_area:assignment_substitute", args=[past.pk]))

    def test_assignment_form_labels_participant_in_portuguese(self):
        page = self._page("lider")
        self.assertContains(page, "Participante")
        self.assertNotContains(page, "Participant:")
