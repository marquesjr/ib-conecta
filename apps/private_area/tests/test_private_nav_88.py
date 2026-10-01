from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role

User = get_user_model()


def login(client, username, role):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    client.login(username=username, password="senha-segura-123")
    return user


class PrivateNavTests(TestCase):
    def test_member_sees_sections_without_events(self):
        login(self.client, "membro", Role.MEMBER)
        body = self.client.get(reverse("private_area:songbook")).content.decode()
        self.assertIn('<nav class="private-nav" aria-label="Área privada">', body)
        for label in ("Início", "Ministérios", "Louvores", "Playlists", "Documentos"):
            self.assertIn(f">{label}</a>", body)
        self.assertNotIn(">Eventos</a>", body)

    def test_events_section_appears_for_the_events_commission(self):
        login(self.client, "comissao", Role.EVENTS_COMMISSION)
        body = self.client.get(reverse("private_area:home")).content.decode()
        self.assertIn(">Eventos</a>", body)

    def test_current_section_is_marked(self):
        login(self.client, "membro", Role.MEMBER)
        body = self.client.get(reverse("private_area:document_library")).content.decode()
        self.assertEqual(body.count('aria-current="page"'), 1)
        self.assertIn('href="/area-privada/documentos/" aria-current="page">Documentos', body)

    def test_nav_is_absent_outside_the_private_area(self):
        login(self.client, "membro", Role.MEMBER)
        self.assertNotIn("private-nav", self.client.get(reverse("accounts:account_home")).content.decode())
        self.assertNotIn("private-nav", self.client.get(reverse("home")).content.decode())
