from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import AuditLog, Role
from apps.private_area.models import DocumentAudience, PrivateDocument

User = get_user_model()


def make_user(username: str, role: str):
    user = User.objects.create_user(username=username, password="senha-segura-123")
    user.profile.role = role
    user.profile.save()
    return user


def make_document(*, title: str, audience: str, filename: str = "arquivo.pdf") -> PrivateDocument:
    return PrivateDocument.objects.create(
        title=title,
        description="Material interno",
        audience=audience,
        file=SimpleUploadedFile(filename, b"%PDF-1.4 conteudo-privado", content_type="application/pdf"),
    )


class PrivateDocumentLibraryTests(TestCase):
    def setUp(self):
        self.member_doc = make_document(
            title="Comunicado aos membros",
            audience=DocumentAudience.MEMBERS,
        )
        self.content_doc = make_document(
            title="Pauta da comunicação",
            audience=DocumentAudience.CONTENT,
        )
        self.finance_doc = make_document(
            title="Relatório da tesouraria",
            audience=DocumentAudience.FINANCES,
        )
        self.admin_doc = make_document(
            title="Ata da administração",
            audience=DocumentAudience.ADMIN,
        )

    def test_visitor_is_blocked_from_document_library_and_download(self):
        library = self.client.get(reverse("private_area:document_library"))
        self.assertEqual(library.status_code, 302)
        self.assertIn(reverse("accounts:login"), library.url)

        download = self.client.get(
            reverse("private_area:document_download", args=[self.member_doc.pk])
        )
        self.assertEqual(download.status_code, 302)
        self.assertIn(reverse("accounts:login"), download.url)

        upload = self.client.get(reverse("private_area:document_upload"))
        self.assertEqual(upload.status_code, 302)
        self.assertIn(reverse("accounts:login"), upload.url)

    def test_member_sees_only_member_documents(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("private_area:document_library"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comunicado aos membros")
        self.assertNotContains(response, "Pauta da comunicação")
        self.assertNotContains(response, "Relatório da tesouraria")
        self.assertNotContains(response, "Ata da administração")

    def test_member_can_download_member_document_and_not_finance_document(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")

        allowed = self.client.get(
            reverse("private_area:document_download", args=[self.member_doc.pk])
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(b"".join(allowed.streaming_content), b"%PDF-1.4 conteudo-privado")

        denied = self.client.get(
            reverse("private_area:document_download", args=[self.finance_doc.pk])
        )
        self.assertEqual(denied.status_code, 403)

    def test_treasury_sees_member_and_finance_documents(self):
        make_user("tesouraria", Role.TREASURY)
        self.client.login(username="tesouraria", password="senha-segura-123")
        response = self.client.get(reverse("private_area:document_library"))
        self.assertContains(response, "Comunicado aos membros")
        self.assertContains(response, "Relatório da tesouraria")
        self.assertNotContains(response, "Pauta da comunicação")
        self.assertNotContains(response, "Ata da administração")

    def test_communication_sees_member_and_content_documents(self):
        make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")
        response = self.client.get(reverse("private_area:document_library"))
        self.assertContains(response, "Comunicado aos membros")
        self.assertContains(response, "Pauta da comunicação")
        self.assertNotContains(response, "Relatório da tesouraria")
        self.assertNotContains(response, "Ata da administração")

    def test_admin_sees_all_documents(self):
        make_user("admin", Role.ADMIN)
        self.client.login(username="admin", password="senha-segura-123")
        response = self.client.get(reverse("private_area:document_library"))
        self.assertContains(response, "Comunicado aos membros")
        self.assertContains(response, "Pauta da comunicação")
        self.assertContains(response, "Relatório da tesouraria")
        self.assertContains(response, "Ata da administração")

    def test_private_document_is_not_served_as_public_media(self):
        self.assertFalse(
            Path(self.member_doc.file.path).is_relative_to(Path(settings.MEDIA_ROOT))
        )
        public = self.client.get(f"/media/{self.member_doc.file.name}")
        self.assertNotEqual(public.status_code, 200)

    def test_member_cannot_upload_documents(self):
        make_user("membro", Role.MEMBER)
        self.client.login(username="membro", password="senha-segura-123")
        response = self.client.get(reverse("private_area:document_upload"))
        self.assertEqual(response.status_code, 403)

    def test_communication_can_upload_a_restricted_document(self):
        make_user("comms", Role.COMMUNICATION)
        self.client.login(username="comms", password="senha-segura-123")
        response = self.client.post(
            reverse("private_area:document_upload"),
            {
                "title": "Circular pastoral",
                "description": "Uso interno",
                "audience": DocumentAudience.CONTENT,
                "file": SimpleUploadedFile(
                    "circular.pdf",
                    b"%PDF-1.4 nova-circular",
                    content_type="application/pdf",
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        document = PrivateDocument.objects.get(title="Circular pastoral")
        self.assertEqual(document.audience, DocumentAudience.CONTENT)
        entry = AuditLog.objects.filter(action="document_uploaded").latest("created_at")
        self.assertEqual(entry.metadata.get("document_id"), document.pk)
        self.assertEqual(entry.metadata.get("title"), "Circular pastoral")
