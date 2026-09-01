"""Cliente da API oficial do Instagram e sincronização do acervo.

Dois caminhos oficiais existem, e o correto depende do tipo de conta da igreja:

- ``instagram_login`` (host ``graph.instagram.com``): Login Empresarial do Instagram,
  escopo ``instagram_business_basic``. Conta Criador ou Empresa que **não** precisa
  estar ligada a uma Página do Facebook. É o caminho leve.
- ``facebook_login`` (host ``graph.facebook.com``): Login do Facebook, escopos
  ``instagram_basic``, ``pages_show_list`` e ``pages_read_engagement``, para conta
  Empresa já administrada por uma Página.

Conta pessoal não tem acesso a nenhuma API oficial desde o encerramento do Basic
Display; não há caminho legítimo que contorne isso.

As imagens são baixadas e guardadas localmente porque as URLs do CDN da Meta
expiram. Nesta superfície a fotografia é o material principal da página, então
imagem quebrada seria a falha mais visível possível.
"""

from __future__ import annotations

import json
import logging
import mimetypes
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

logger = logging.getLogger(__name__)

GRAPH_VERSION = "v25.0"
INSTAGRAM_HOST = "https://graph.instagram.com"
FACEBOOK_HOST = "https://graph.facebook.com"

MEDIA_FIELDS = "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp"

TIMEOUT = 20
MAX_IMAGE_BYTES = 12 * 1024 * 1024


class InstagramError(RuntimeError):
    """Falha ao falar com a API. Sempre tratada, nunca propagada para a requisição."""


@dataclass(frozen=True)
class RemoteFrame:
    remote_id: str
    image_url: str
    permalink: str
    caption: str
    taken_at: datetime


def _get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise InstagramError(f"HTTP {exc.code} da API: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise InstagramError(f"Não foi possível falar com a API: {exc}") from exc


def _short_caption(caption: str) -> str:
    """A legenda a nanquim é uma anotação curta, não o texto inteiro do post."""
    first_line = (caption or "").strip().splitlines()
    if not first_line:
        return ""
    text = " ".join(first_line[0].split())
    text = text.lstrip("#").strip()
    return text[:117] + "…" if len(text) > 118 else text


def _media_url(item: dict) -> str:
    """Escolhe a URL utilizável. ``media_url`` some quando a Meta marca direito autoral."""
    if item.get("media_type") == "VIDEO":
        return item.get("thumbnail_url") or ""
    return item.get("media_url") or item.get("thumbnail_url") or ""


def fetch_media(*, mode: str, token: str, user_id: str = "", limit: int = 24) -> list[RemoteFrame]:
    """Busca as mídias mais recentes. Levanta ``InstagramError`` em qualquer falha."""
    if not token:
        raise InstagramError("Nenhum token de acesso cadastrado.")

    params = {"fields": MEDIA_FIELDS, "limit": str(limit), "access_token": token}
    if mode == "instagram_login":
        url = f"{INSTAGRAM_HOST}/me/media?{urllib.parse.urlencode(params)}"
    elif mode == "facebook_login":
        if not user_id:
            raise InstagramError("O Login do Facebook exige o ID da conta do Instagram.")
        url = f"{FACEBOOK_HOST}/{GRAPH_VERSION}/{user_id}/media?{urllib.parse.urlencode(params)}"
    else:
        raise InstagramError(f"Origem do acervo desconhecida: {mode!r}")

    payload = _get_json(url)
    frames = []
    for item in payload.get("data", []):
        image_url = _media_url(item)
        if not image_url:
            # Mídia com direito autoral marcado vem sem URL. Ignorar é o comportamento correto.
            continue
        taken_at = parse_datetime(item.get("timestamp") or "") or timezone.now()
        frames.append(
            RemoteFrame(
                remote_id=str(item.get("id") or ""),
                image_url=image_url,
                permalink=item.get("permalink") or "",
                caption=_short_caption(item.get("caption") or ""),
                taken_at=taken_at,
            )
        )
    return [frame for frame in frames if frame.remote_id]


def refresh_token(*, mode: str, token: str) -> tuple[str, datetime | None]:
    """Renova o token de longa duração. Retorna o novo token e a nova expiração."""
    if mode == "instagram_login":
        params = {"grant_type": "ig_refresh_token", "access_token": token}
        payload = _get_json(f"{INSTAGRAM_HOST}/refresh_access_token?{urllib.parse.urlencode(params)}")
    elif mode == "facebook_login":
        app_id = getattr(settings, "INSTAGRAM_APP_ID", "")
        app_secret = getattr(settings, "INSTAGRAM_APP_SECRET", "")
        if not (app_id and app_secret):
            raise InstagramError(
                "A renovação pelo Login do Facebook exige INSTAGRAM_APP_ID e INSTAGRAM_APP_SECRET."
            )
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": token,
        }
        payload = _get_json(
            f"{FACEBOOK_HOST}/{GRAPH_VERSION}/oauth/access_token?{urllib.parse.urlencode(params)}"
        )
    else:
        raise InstagramError(f"Origem do acervo desconhecida: {mode!r}")

    new_token = payload.get("access_token")
    if not new_token:
        raise InstagramError("A API não devolveu um token novo.")
    expires_in = payload.get("expires_in")
    expires_at = timezone.now() + timedelta(seconds=int(expires_in)) if expires_in else None
    return new_token, expires_at


def _download(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"Accept": "image/*"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip()
            data = response.read(MAX_IMAGE_BYTES + 1)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise InstagramError(f"Falha ao baixar a imagem: {exc}") from exc
    if len(data) > MAX_IMAGE_BYTES:
        raise InstagramError("Imagem maior que o limite aceito.")
    extension = mimetypes.guess_extension(content_type) or ".jpg"
    if extension == ".jpe":
        extension = ".jpg"
    return data, extension


def sync() -> dict:
    """Sincroniza o acervo com o Instagram da igreja.

    Nunca levanta: devolve um resumo e registra o erro na credencial, para que a
    página continue servindo a galeria curada quando a Meta estiver indisponível.
    """
    from apps.public.models import ArchiveFrame, ChurchSettings, InstagramCredential

    summary = {"created": 0, "updated": 0, "skipped": 0, "error": ""}

    church = ChurchSettings.objects.first()
    if church is None:
        summary["error"] = "Configurações da igreja não cadastradas."
        return summary

    mode = church.instagram_mode
    if mode == ChurchSettings.InstagramMode.OFF:
        summary["error"] = "Acervo do Instagram desligado nas configurações."
        return summary

    credential = InstagramCredential.current()
    if credential is None or not credential.access_token:
        summary["error"] = "Nenhuma credencial do Instagram cadastrada."
        return summary

    try:
        frames = fetch_media(
            mode=mode,
            token=credential.access_token,
            user_id=church.instagram_user_id,
            limit=max(church.archive_frame_count * 2, 12),
        )
    except InstagramError as exc:
        logger.warning("Sincronização do Instagram falhou: %s", exc)
        summary["error"] = str(exc)
        credential.last_sync_error = str(exc)
        credential.save(update_fields=["last_sync_error"])
        return summary

    for frame in frames:
        existing = ArchiveFrame.objects.filter(
            source=ArchiveFrame.Source.INSTAGRAM, remote_id=frame.remote_id
        ).first()
        if existing is not None:
            changed = []
            if existing.caption != frame.caption:
                existing.caption = frame.caption
                changed.append("caption")
            if existing.permalink != frame.permalink:
                existing.permalink = frame.permalink
                changed.append("permalink")
            if changed:
                existing.save(update_fields=changed)
                summary["updated"] += 1
            else:
                summary["skipped"] += 1
            continue

        try:
            data, extension = _download(frame.image_url)
        except InstagramError as exc:
            logger.warning("Imagem %s não baixou: %s", frame.remote_id, exc)
            summary["skipped"] += 1
            continue

        record = ArchiveFrame(
            source=ArchiveFrame.Source.INSTAGRAM,
            remote_id=frame.remote_id,
            caption=frame.caption,
            alt_text=frame.caption,
            permalink=frame.permalink,
            taken_at=frame.taken_at,
        )
        name = f"{slugify(frame.remote_id) or 'quadro'}{extension}"
        record.image.save(name, ContentFile(data), save=False)
        record.save()
        summary["created"] += 1

    credential.last_sync_at = timezone.now()
    credential.last_sync_error = ""
    credential.save(update_fields=["last_sync_at", "last_sync_error"])
    return summary
