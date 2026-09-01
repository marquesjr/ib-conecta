"""Renova o token de longa duração antes do vencimento.

Rode isto num agendador. Um token de 60 dias que ninguém renova é o motivo mais
comum de um acervo do Instagram parar de atualizar sem nenhum erro visível no site.
"""

from django.core.management.base import BaseCommand, CommandError

from apps.public.instagram import InstagramError, refresh_token
from apps.public.models import ChurchSettings, InstagramCredential


class Command(BaseCommand):
    help = "Renova o token de longa duração da API do Instagram."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Renova mesmo que o token ainda esteja longe de vencer.",
        )
        parser.add_argument(
            "--within-days",
            dest="within_days",
            type=int,
            default=10,
            help="Renova quando faltarem até estes dias para vencer (padrão 10).",
        )

    def handle(self, *args, **options):
        church = ChurchSettings.objects.first()
        if church is None:
            raise CommandError("Configurações da igreja não cadastradas.")
        if church.instagram_mode == ChurchSettings.InstagramMode.OFF:
            self.stdout.write("Acervo do Instagram desligado; nada a renovar.")
            return

        credential = InstagramCredential.current()
        if credential is None or not credential.access_token:
            raise CommandError("Nenhuma credencial cadastrada. Use set_instagram_token primeiro.")

        if not options["force"] and not credential.is_expiring(options["within_days"]):
            self.stdout.write(
                f"Token válido até {credential.expires_at:%d/%m/%Y}; fora da janela de renovação."
            )
            return

        try:
            token, expires_at = refresh_token(
                mode=church.instagram_mode, token=credential.access_token
            )
        except InstagramError as exc:
            raise CommandError(f"Renovação falhou: {exc}") from exc

        from django.utils import timezone

        credential.access_token = token
        credential.expires_at = expires_at
        credential.refreshed_at = timezone.now()
        credential.save(update_fields=["access_token", "expires_at", "refreshed_at"])

        quando = f"{expires_at:%d/%m/%Y}" if expires_at else "sem data informada pela Meta"
        self.stdout.write(self.style.SUCCESS(f"Token renovado. Nova validade: {quando}."))
