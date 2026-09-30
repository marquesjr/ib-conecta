from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role
from apps.private_area.models import (
    BudgetLineStatus,
    EventBudgetLine,
    EventChecklistItem,
    EventOperation,
    EventTask,
)
from apps.private_area.tests.test_event_operations import make_user, publish_event
from apps.public.models import EventRegistration


class EventOperationLayoutTests(TestCase):
    def setUp(self):
        self.coordinator = make_user("coordenador", Role.EVENTS_COMMISSION)
        self.tesoureiro = make_user("tesoureiro", Role.TREASURY)
        event = publish_event(title="Encontro de casais", slug="encontro-casais")
        self.operation = EventOperation.objects.create(public_event=event, created_by=self.coordinator)
        EventTask.objects.create(operation=self.operation, title="Comprar copos", assignee=self.coordinator)
        EventTask.objects.create(
            operation=self.operation, title="Reservar salão", assignee=self.coordinator, done=True
        )
        EventTask.objects.create(operation=self.operation, title="Imprimir crachás", assignee=self.coordinator)
        EventChecklistItem.objects.create(operation=self.operation, label="Conferir som", assignee=self.coordinator)
        EventBudgetLine.objects.create(
            operation=self.operation,
            description="Coffee break",
            amount=Decimal("1500.00"),
            status=BudgetLineStatus.APPROVED,
        )
        EventBudgetLine.objects.create(
            operation=self.operation, description="Decoração", amount=Decimal("80.50")
        )
        EventRegistration.objects.create(event=event, name="Maria", email="maria@example.com")
        EventRegistration.objects.create(
            event=event,
            name="João",
            email="joao@example.com",
            status=EventRegistration.Status.CANCELLED,
        )
        self.url = reverse("private_area:event_operation_detail", args=[self.operation.pk])

    def test_summary_shows_event_state_at_a_glance(self):
        self.client.login(username="coordenador", password="senha-segura-123")
        response = self.client.get(self.url)
        summary = response.context["summary"]
        self.assertEqual(summary["open_tasks"], 2)
        self.assertEqual(summary["open_checklist"], 1)
        self.assertEqual(summary["budget_approved"], Decimal("1500.00"))
        self.assertEqual(summary["budget_pending"], Decimal("80.50"))
        self.assertEqual(summary["confirmed_registrations"], 1)
        self.assertContains(response, 'class="operation-summary"')
        self.assertContains(response, "R$ 1.500,00")
        self.assertContains(response, "R$ 80,50 pendente")

    def test_sections_have_anchors(self):
        self.client.login(username="coordenador", password="senha-segura-123")
        response = self.client.get(self.url)
        for anchor in (
            "planejamento",
            "equipes",
            "tarefas",
            "checklist",
            "fornecedores",
            "materiais",
            "orcamento",
            "inscritos",
            "relatorio",
        ):
            self.assertContains(response, f'href="#{anchor}"')
            self.assertContains(response, f'id="{anchor}"')

    def test_forms_start_closed_behind_a_button(self):
        self.client.login(username="coordenador", password="senha-segura-123")
        response = self.client.get(self.url)
        html = response.content.decode()
        self.assertEqual(html.count("<form"), html.count('<details class="add-form">'))
        self.assertNotIn('<details class="add-form" open', html)
        self.assertContains(response, "<summary>Adicionar tarefa</summary>", html=False)

    def test_treasury_sees_only_the_budget_summary(self):
        self.client.login(username="tesoureiro", password="senha-segura-123")
        response = self.client.get(self.url)
        self.assertContains(response, "Orçamento aprovado")
        self.assertNotContains(response, "Tarefas abertas")
        self.assertNotContains(response, 'class="operation-nav"')
