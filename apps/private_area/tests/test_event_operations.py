from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site

from apps.accounts.models import Role
from apps.private_area.models import EventOperation
from apps.public.models import EventIndexPage, EventPage

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


def publish_event(*, title: str, slug: str, days: int = 10, requires_registration: bool = True) -> EventPage:
    root = Site.objects.get(is_default_site=True).root_page
    index = EventIndexPage.objects.filter(slug="agenda").first()
    if index is None:
        index = EventIndexPage(title="Agenda", slug="agenda", intro="")
        root.add_child(instance=index)
        index.save_revision().publish()
    event = EventPage(
        title=title,
        slug=slug,
        starts_at=timezone.now() + timedelta(days=days),
        location="Templo",
        body="<p>Detalhes</p>",
        requires_registration=requires_registration,
    )
    index.add_child(instance=event)
    event.save_revision().publish()
    return event


class EventCalendarAccessTests(TestCase):
    def test_visitor_is_redirected_from_event_calendar(self):
        response = self.client.get(reverse("private_area:event_calendar"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_member_cannot_open_event_calendar(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("private_area:event_calendar"))
        self.assertEqual(response.status_code, 403)

    def test_commission_can_open_the_annual_calendar(self):
        make_user("comissao", Role.EVENTS_COMMISSION)
        self.client.login(username="comissao", password="senha-segura-123")
        response = self.client.get(reverse("private_area:event_calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comissão de eventos")
        self.assertContains(response, "Calendário anual")

    def test_annual_calendar_filters_operations_by_year(self):
        make_user("comissao", Role.EVENTS_COMMISSION)
        this_year = publish_event(title="Encontro de casais", slug="encontro-casais", days=10)
        next_year = publish_event(title="Conferência", slug="conferencia", days=400)
        self.client.login(username="comissao", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": this_year.pk, "notes": ""},
        )
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": next_year.pk, "notes": ""},
        )
        current = timezone.localdate().year
        this_page = self.client.get(reverse("private_area:event_calendar"))
        self.assertContains(this_page, "Encontro de casais")
        self.assertNotContains(this_page, "Conferência")
        next_page = self.client.get(
            reverse("private_area:event_calendar"), {"year": current + 1}
        )
        self.assertContains(next_page, "Conferência")
        self.assertNotContains(next_page, "Encontro de casais")
        self.assertContains(next_page, str(current + 1))


class EventOperationAttachTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.client.login(username="coordenador", password="senha-segura-123")

    def test_coordinator_operates_existing_agenda_event_without_duplicating_it(self):
        page = self.client.get(reverse("private_area:event_operation_create"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Encontro de casais")
        response = self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": "Planejamento da comissão"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventPage.objects.filter(title="Encontro de casais").count(), 1)
        self.assertEqual(EventOperation.objects.count(), 1)
        calendar = self.client.get(reverse("private_area:event_calendar"))
        self.assertContains(calendar, "Encontro de casais")
        detail = self.client.get(response.url)
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Encontro de casais")
        self.assertContains(detail, "Planejamento da comissão")

    def test_coordinator_updates_event_planning(self):
        created = self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": "Rascunho"},
        )
        operation = EventOperation.objects.get()
        updated = self.client.post(
            reverse("private_area:event_planning_update", args=[operation.pk]),
            {"notes": "Equipes confirmadas e local reservado."},
        )
        self.assertEqual(updated.status_code, 302)
        detail = self.client.get(created.url)
        self.assertContains(detail, "Equipes confirmadas e local reservado.")
        self.assertNotContains(detail, "Rascunho")

    def test_member_cannot_create_an_event_operation(self):
        make_user("membro", Role.MEMBER)
        self.client.logout()
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(EventOperation.objects.count(), 0)

    def test_coordinator_creates_a_new_agenda_event_without_a_second_registration(self):
        from apps.public.models import EventRegistration

        starts = timezone.now() + timedelta(days=20)
        response = self.client.post(
            reverse("private_area:event_operation_create"),
            {
                "title": "Retiro de jovens",
                "starts_at": starts.strftime("%Y-%m-%dT%H:%M"),
                "location": "Sítio da igreja",
                "body": "Inscrições abertas",
                "requires_registration": "on",
                "notes": "Equipe de apoio",
            },
        )
        self.assertEqual(response.status_code, 302)
        event = EventPage.objects.get(title="Retiro de jovens")
        self.assertTrue(event.live)
        self.assertTrue(event.requires_registration)
        operation = EventOperation.objects.get()
        self.assertEqual(operation.public_event_id, event.pk)
        public = self.client.post(
            f"{event.url}inscrever/",
            {"name": "Maria Silva", "email": "maria@example.com"},
            follow=True,
        )
        self.assertContains(public, "Inscrição confirmada")
        self.assertTrue(
            EventRegistration.objects.filter(
                event=event, email="maria@example.com"
            ).exists()
        )
        detail = self.client.get(response.url)
        self.assertContains(detail, "Retiro de jovens")
        self.assertContains(detail, "Maria Silva")


class EventTeamTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.client.login(username="coordenador", password="senha-segura-123")
        created = self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": "Planejamento"},
        )
        self.assertEqual(created.status_code, 302)
        self.operation = EventOperation.objects.get()

    def test_coordinator_manages_event_teams(self):
        added = self.client.post(
            reverse("private_area:event_team_add", args=[self.operation.pk]),
            {"name": "Recepção"},
        )
        self.assertEqual(added.status_code, 302)
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "Recepção")
        from apps.private_area.models import EventTeam

        team = EventTeam.objects.get(name="Recepção")
        member = self.client.post(
            reverse("private_area:event_team_member_add", args=[team.pk]),
            {"user": self.ana.pk},
        )
        self.assertEqual(member.status_code, 302)
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "ana")

    def test_member_cannot_manage_teams(self):
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:event_team_add", args=[self.operation.pk]),
            {"name": "Cozinha"},
        )
        self.assertEqual(response.status_code, 403)


class EventTaskTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.bruno = make_user("bruno", Role.MEMBER)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.operation = EventOperation.objects.get()

    def test_assigned_member_updates_task_and_checklist(self):
        from apps.private_area.models import EventChecklistItem, EventTask

        task_added = self.client.post(
            reverse("private_area:event_task_add", args=[self.operation.pk]),
            {"title": "Comprar copos", "assignee": self.ana.pk},
        )
        self.assertEqual(task_added.status_code, 302)
        check_added = self.client.post(
            reverse("private_area:event_checklist_add", args=[self.operation.pk]),
            {"label": "Conferir som", "assignee": self.ana.pk},
        )
        self.assertEqual(check_added.status_code, 302)
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "Comprar copos")
        self.assertContains(detail, "Conferir som")

        task = EventTask.objects.get()
        item = EventChecklistItem.objects.get()
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        task_page = self.client.get(
            reverse("private_area:event_task_update", args=[task.pk])
        )
        self.assertEqual(task_page.status_code, 200)
        self.assertContains(task_page, "Comprar copos")
        self.client.post(
            reverse("private_area:event_task_update", args=[task.pk]),
            {"action": "complete"},
        )
        task.refresh_from_db()
        self.assertTrue(task.done)
        check_page = self.client.get(
            reverse("private_area:event_checklist_update", args=[item.pk])
        )
        self.assertEqual(check_page.status_code, 200)
        self.assertContains(check_page, "Conferir som")
        self.client.post(
            reverse("private_area:event_checklist_update", args=[item.pk]),
            {"action": "complete"},
        )
        item.refresh_from_db()
        self.assertTrue(item.done)

    def test_other_member_cannot_update_someone_elses_task(self):
        from apps.private_area.models import EventTask

        self.client.post(
            reverse("private_area:event_task_add", args=[self.operation.pk]),
            {"title": "Montar palco", "assignee": self.ana.pk},
        )
        task = EventTask.objects.get()
        self.client.logout()
        self.client.login(username="bruno", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:event_task_update", args=[task.pk]),
            {"action": "complete"},
        )
        self.assertEqual(response.status_code, 403)
        task.refresh_from_db()
        self.assertFalse(task.done)


class EventLogisticsTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.operation = EventOperation.objects.get()

    def test_coordinator_records_suppliers_and_materials(self):
        supplier = self.client.post(
            reverse("private_area:event_supplier_add", args=[self.operation.pk]),
            {"name": "Buffet Central", "contact": "27999990000", "notes": "Coffee break"},
        )
        self.assertEqual(supplier.status_code, 302)
        material = self.client.post(
            reverse("private_area:event_material_add", args=[self.operation.pk]),
            {"name": "Cadeiras", "quantity": "40", "notes": ""},
        )
        self.assertEqual(material.status_code, 302)
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "Buffet Central")
        self.assertContains(detail, "Cadeiras")
        self.assertContains(detail, "40")

    def test_member_cannot_add_suppliers(self):
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:event_supplier_add", args=[self.operation.pk]),
            {"name": "Som e luz", "contact": "", "notes": ""},
        )
        self.assertEqual(response.status_code, 403)


class EventBudgetTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.tesoureiro = make_user("tesoureiro", Role.TREASURY)
        self.ana = make_user("ana", Role.MEMBER)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.operation = EventOperation.objects.get()

    def test_treasury_views_and_approves_financial_lines(self):
        from apps.private_area.models import BudgetLineStatus, EventBudgetLine

        added = self.client.post(
            reverse("private_area:event_budget_add", args=[self.operation.pk]),
            {"description": "Coffee break", "amount": "150.00"},
        )
        self.assertEqual(added.status_code, 302)
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "Coffee break")
        self.assertContains(detail, "150")
        line = EventBudgetLine.objects.get()
        self.assertEqual(line.status, BudgetLineStatus.PENDING)

        self.client.logout()
        self.client.login(username="tesoureiro", password="senha-segura-123")
        calendar = self.client.get(reverse("private_area:event_calendar"))
        self.assertEqual(calendar.status_code, 200)
        self.assertContains(calendar, "Encontro de casais")
        treasury_detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertEqual(treasury_detail.status_code, 200)
        self.assertContains(treasury_detail, "Coffee break")
        self.assertContains(treasury_detail, "150")
        self.assertContains(treasury_detail, "Orçamento")
        self.assertNotContains(treasury_detail, "Equipes")
        self.assertNotContains(treasury_detail, "Tarefas")
        self.assertNotContains(treasury_detail, "Fornecedores")
        approved = self.client.post(
            reverse("private_area:event_budget_review", args=[line.pk]),
            {"action": "approve"},
        )
        self.assertEqual(approved.status_code, 302)
        line.refresh_from_db()
        self.assertEqual(line.status, BudgetLineStatus.APPROVED)

    def test_coordinator_cannot_approve_budget(self):
        from apps.private_area.models import BudgetLineStatus, EventBudgetLine

        self.client.post(
            reverse("private_area:event_budget_add", args=[self.operation.pk]),
            {"description": "Som", "amount": "80.00"},
        )
        line = EventBudgetLine.objects.get()
        response = self.client.post(
            reverse("private_area:event_budget_review", args=[line.pk]),
            {"action": "approve"},
        )
        self.assertEqual(response.status_code, 403)
        line.refresh_from_db()
        self.assertEqual(line.status, BudgetLineStatus.PENDING)

    def test_member_cannot_see_or_approve_budget(self):
        from apps.private_area.models import BudgetLineStatus, EventBudgetLine

        self.client.post(
            reverse("private_area:event_budget_add", args=[self.operation.pk]),
            {"description": "Faixas", "amount": "40.00"},
        )
        line = EventBudgetLine.objects.get()
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        calendar = self.client.get(reverse("private_area:event_calendar"))
        self.assertEqual(calendar.status_code, 403)
        response = self.client.post(
            reverse("private_area:event_budget_review", args=[line.pk]),
            {"action": "approve"},
        )
        self.assertEqual(response.status_code, 403)
        line.refresh_from_db()
        self.assertEqual(line.status, BudgetLineStatus.PENDING)


class EventRegistrantMessageTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        from apps.public.models import EventRegistration

        EventRegistration.objects.create(
            event=self.event,
            name="Ana Costa",
            email="ana@example.com",
        )
        EventRegistration.objects.create(
            event=self.event,
            name="Bruno Cancelado",
            email="bruno@example.com",
            status=EventRegistration.Status.CANCELLED,
        )
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.operation = EventOperation.objects.get()

    def test_coordinator_messages_confirmed_registrants(self):
        from django.core import mail

        response = self.client.post(
            reverse("private_area:event_registrant_message", args=[self.operation.pk]),
            {
                "subject": "Horário de chegada",
                "body": "Cheguem às 8h.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Horário de chegada")
        self.assertIn("Cheguem às 8h.", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])

    def test_member_cannot_message_registrants(self):
        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:event_registrant_message", args=[self.operation.pk]),
            {"subject": "Oi", "body": "Texto"},
        )
        self.assertEqual(response.status_code, 403)


class EventReportTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.ana = make_user("ana", Role.MEMBER)
        self.tesoureiro = make_user("tesoureiro", Role.TREASURY)
        self.event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.client.login(username="coordenador", password="senha-segura-123")
        self.client.post(
            reverse("private_area:event_operation_create"),
            {"public_event": self.event.pk, "notes": ""},
        )
        self.operation = EventOperation.objects.get()

    def test_coordinator_saves_final_report_and_restricted_document(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from apps.private_area.models import EventOperationDocument

        saved = self.client.post(
            reverse("private_area:event_final_report", args=[self.operation.pk]),
            {"final_report": "Ata: 40 presentes e orçamento dentro do previsto."},
        )
        self.assertEqual(saved.status_code, 302)
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "40 presentes")
        uploaded = self.client.post(
            reverse("private_area:event_document_upload", args=[self.operation.pk]),
            {
                "title": "Ata da comissão",
                "file": SimpleUploadedFile(
                    "ata.pdf",
                    b"%PDF-1.4 ata-privada",
                    content_type="application/pdf",
                ),
            },
        )
        self.assertEqual(uploaded.status_code, 302)
        document = EventOperationDocument.objects.get()
        detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertContains(detail, "Ata da comissão")
        download = self.client.get(
            reverse("private_area:event_document_download", args=[document.pk])
        )
        self.assertEqual(download.status_code, 200)

        self.client.logout()
        self.client.login(username="ana", password="senha-segura-123")
        denied = self.client.get(
            reverse("private_area:event_document_download", args=[document.pk])
        )
        self.assertEqual(denied.status_code, 403)
        self.client.logout()
        self.client.login(username="tesoureiro", password="senha-segura-123")
        treasury_detail = self.client.get(
            reverse("private_area:event_operation_detail", args=[self.operation.pk])
        )
        self.assertEqual(treasury_detail.status_code, 200)
        self.assertNotContains(treasury_detail, "40 presentes")
        self.assertNotContains(treasury_detail, "Ata da comissão")
        treasury_download = self.client.get(
            reverse("private_area:event_document_download", args=[document.pk])
        )
        self.assertEqual(treasury_download.status_code, 403)
