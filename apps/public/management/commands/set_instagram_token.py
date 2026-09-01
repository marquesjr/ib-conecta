"""Cadastra o token de longa duração do Instagram fora do painel do CMS."""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.public.models import InstagramCredential


class Command(BaseCommand):
    help = (
        "Cadastra ou substitui o token de longa duração da API do Instagram. "
        "Prefira passar o token por variável de ambiente a digitá-lo na linha de comando, "
        "porque o histórico do shell guarda o que foi digitado."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--token",
            dest="token",
            default="",
            help="Token de longa duração. Se omitido, é lido de INSTAGRAM_ACCESS_TOKEN.",
        )
        parser.add_argument(
            "--expires-in-days",
            dest="expires_in_days",
            type=int,
            default=60,
            help="Validade em dias informada pela Meta (padrão 60).",
        )

    def handle(self, *args, **options):
        import os

        token = options["token"] or os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
        if not token:
            raise CommandError(
                "Nenhum token informado. Use --token ou defina INSTAGRAM_ACCESS_TOKEN."
            )

        expires_at = timezone.now() + timedelta(days=options["expires_in_days"])
        credential = InstagramCredential.current()
        if credential is None:
            credential = InstagramCredential(access_token=token)
        credential.access_token = token
        credential.expires_at = expires_at
        credential.refreshed_at = timezone.now()
        credential.last_sync_error = ""
        credential.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Token cadastrado. Expira em {expires_at:%d/%m/%Y}. "
                "Renove com refresh_instagram_token antes dessa data."
            )
        )
