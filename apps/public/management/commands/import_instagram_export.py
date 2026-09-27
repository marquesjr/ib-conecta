"""Importa fotografias da exportação oficial de dados do Instagram."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site

from apps.public.instagram import DEFAULT_INSTAGRAM_HANDLE, DEFAULT_INSTAGRAM_URL, normalize_handle
from apps.public.instagram_export import import_export
from apps.public.models import ChurchSettings


class Command(BaseCommand):
    help = (
        "Lê a exportação JSON/ZIP que a Meta entrega ao dono da conta "
        "(Download Your Information) e grava as fotografias nos Quadros do acervo. "
        "Não usa raspagem nem token. Passos para pedir o arquivo: docs/ops/instagram-acervo.md."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            help="Pasta extraída ou ZIP da exportação oficial (JSON, não HTML).",
        )
        parser.add_argument(
            "--handle",
            dest="handle",
            default="",
            help="Arroba da conta, sem @. Padrão: configuração da igreja ou igrejabatista.santaleopoldina.",
        )
        parser.add_argument(
            "--credit",
            dest="credit",
            default="",
            help="Crédito visível. Padrão: Instagram @<handle>.",
        )
        parser.add_argument(
            "--limit",
            dest="limit",
            type=int,
            default=200,
            help="Máximo de fotografias (as mais recentes primeiro). Padrão 200.",
        )
        parser.add_argument(
            "--include-stories",
            dest="include_stories",
            action="store_true",
            help="Também importa stories que vierem como imagem na exportação.",
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Só lista o que seria importado, sem gravar.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        handle = normalize_handle(options["handle"])
        if not handle:
            site = Site.objects.filter(is_default_site=True).first()
            church = ChurchSettings.for_site(site) if site else ChurchSettings.objects.first()
            handle = normalize_handle(getattr(church, "instagram_handle", "") or "") or DEFAULT_INSTAGRAM_HANDLE

        summary = import_export(
            path,
            handle=handle,
            credit=options["credit"],
            limit=options["limit"],
            include_stories=options["include_stories"],
            dry_run=options["dry_run"],
        )
        if summary["error"]:
            raise CommandError(summary["error"])

        if options["dry_run"]:
            self.stdout.write(f"Encontradas {summary['found']} fotografia(s). Nada foi gravado.")
            for item in summary["items"][:20]:
                when = item.taken_at.strftime("%Y-%m-%d") if item.taken_at else "?"
                caption = item.caption or "(sem legenda)"
                self.stdout.write(f"  {when}  {caption}  {item.path.name}")
            if summary["found"] > 20:
                self.stdout.write(f"  … e mais {summary['found'] - 20}.")
            return

        self.stdout.write(
            "Quadros novos: {created} | atualizados: {updated} | ignorados: {skipped} | lidos: {found}".format(
                **summary
            )
        )
        self.stdout.write(
            "Revise em Quadros do acervo e na home. "
            f"Se o link do perfil não aparecer, grave {DEFAULT_INSTAGRAM_URL} nas configurações da igreja."
        )
