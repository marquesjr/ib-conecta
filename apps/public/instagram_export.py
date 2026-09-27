"""Importação da exportação oficial de dados do Instagram (Download Your Information).

A Meta não oferece API pública para a conta de outra pessoa, e conta pessoal não
tem Graph API. O caminho legítimo sem token é a exportação JSON que o dono da
conta pede em Contas centrais → Suas informações → Baixar informações.

Não há raspagem: só lemos arquivos que a igreja baixou da própria Meta.
"""

from __future__ import annotations

import hashlib
import json
import logging
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

from django.utils import timezone

from apps.public.instagram import (
    DEFAULT_INSTAGRAM_HANDLE,
    _short_caption,
    archive_credit,
    upsert_archive_frame,
)

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
SKIP_JSON_HINTS = (
    "ads_information",
    "likes",
    "comments",
    "followers",
    "following",
    "login",
    "security",
    "messages",
    "sticker",
)


@dataclass(frozen=True)
class ExportItem:
    remote_id: str
    path: Path
    caption: str
    taken_at: datetime
    kind: str  # "post" | "story"


def fix_instagram_text(text: str) -> str:
    """A exportação da Meta costuma gravar UTF-8 como se fosse Latin-1."""
    raw = (text or "").strip()
    if not raw:
        return ""
    try:
        return raw.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return raw


def export_remote_id(uri: str) -> str:
    digest = hashlib.sha256(uri.encode("utf-8")).hexdigest()[:40]
    return f"export:{digest}"


def _looks_like_posts_manifest(path: Path) -> bool:
    name = path.name.lower()
    blob = str(path).replace("\\", "/").lower()
    if any(hint in blob for hint in SKIP_JSON_HINTS):
        return False
    if name.startswith("posts_") and name.endswith(".json"):
        return True
    if name in {"posts.json", "media.json"}:
        return True
    return False


def _looks_like_stories_manifest(path: Path) -> bool:
    name = path.name.lower()
    blob = str(path).replace("\\", "/").lower()
    if "sticker" in blob:
        return False
    return name.endswith(".json") and "stor" in name


def _parse_timestamp(value) -> datetime:
    if value in (None, ""):
        return timezone.now()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(int(value), tz=dt_timezone.utc)
    if isinstance(value, str) and value.isdigit():
        return datetime.fromtimestamp(int(value), tz=dt_timezone.utc)
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, dt_timezone.utc)
    return parsed


def _resolve_media_path(export_root: Path, uri: str) -> Path | None:
    relative = Path(str(uri).replace("\\", "/").lstrip("/"))
    candidates = [
        export_root / relative,
        export_root / relative.name,
    ]
    # ZIP da Meta às vezes envolve tudo numa pasta datada.
    if relative.parts:
        candidates.extend(export_root.glob(f"*/{relative.as_posix()}"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    matches = list(export_root.rglob(relative.name))
    if len(matches) == 1 and matches[0].is_file():
        return matches[0]
    return None


def _iter_media_entries(payload) -> list[tuple[dict, dict, str]]:
    """Devolve (post, media, kind) a partir dos formatos JSON da Meta."""
    rows: list[tuple[dict, dict, str]] = []

    def add_media(post: dict, media: dict, kind: str) -> None:
        if isinstance(media, dict) and media.get("uri"):
            rows.append((post, media, kind))

    if isinstance(payload, dict):
        for key, kind in (("photos", "post"), ("videos", "post"), ("stories", "story")):
            for item in payload.get(key) or []:
                if not isinstance(item, dict):
                    continue
                if item.get("uri") or item.get("path"):
                    media = dict(item)
                    if "uri" not in media and "path" in media:
                        media["uri"] = media["path"]
                    add_media(item, media, kind)
                for media in item.get("media") or []:
                    add_media(item, media, kind)
        payload = payload.get("data") or payload.get("posts") or []

    if isinstance(payload, list):
        for post in payload:
            if not isinstance(post, dict):
                continue
            media_list = post.get("media")
            if isinstance(media_list, list) and media_list:
                for media in media_list:
                    add_media(post, media, "post")
            elif post.get("uri") or post.get("path"):
                media = dict(post)
                if "uri" not in media and "path" in media:
                    media["uri"] = media["path"]
                add_media(post, media, "post")
    return rows


def parse_export(export_root: Path, *, include_stories: bool = False) -> list[ExportItem]:
    """Lê os JSON da exportação e devolve só arquivos de imagem existentes."""
    items: list[ExportItem] = []
    seen: set[str] = set()
    json_files = sorted(path for path in export_root.rglob("*.json") if path.is_file())
    for manifest in json_files:
        is_posts = _looks_like_posts_manifest(manifest)
        is_stories = _looks_like_stories_manifest(manifest)
        if not is_posts and not (include_stories and is_stories):
            continue
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            logger.warning("JSON da exportação ilegível (%s): %s", manifest, exc)
            continue
        kind_override = "story" if is_stories else None
        for post, media, kind in _iter_media_entries(payload):
            kind = kind_override or kind
            if kind == "story" and not include_stories:
                continue
            uri = str(media.get("uri") or "")
            suffix = Path(uri).suffix.lower()
            if suffix == ".jpeg":
                suffix = ".jpg"
            if suffix not in IMAGE_SUFFIXES:
                continue
            path = _resolve_media_path(export_root, uri)
            if path is None:
                logger.warning("Arquivo da exportação não encontrado: %s", uri)
                continue
            remote_id = export_remote_id(uri)
            if remote_id in seen:
                continue
            seen.add(remote_id)
            caption_raw = media.get("title") or post.get("title") or media.get("caption") or post.get("caption") or ""
            taken = media.get("creation_timestamp") or post.get("creation_timestamp") or media.get("taken_at")
            items.append(
                ExportItem(
                    remote_id=remote_id,
                    path=path,
                    caption=_short_caption(fix_instagram_text(str(caption_raw))),
                    taken_at=_parse_timestamp(taken),
                    kind=kind,
                )
            )
    items.sort(key=lambda item: item.taken_at, reverse=True)
    return items


def open_export(path: Path) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    """Aceita pasta extraída ou ZIP oficial. O caller fecha o TemporaryDirectory."""
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    if path.is_dir():
        return path, None
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Nem pasta nem ZIP da Meta: {path}")
    tmp = tempfile.TemporaryDirectory(prefix="ig-export-")
    try:
        with zipfile.ZipFile(path) as archive:
            archive.extractall(tmp.name)
    except Exception:
        tmp.cleanup()
        raise
    return Path(tmp.name), tmp


def import_export(
    path: Path,
    *,
    handle: str = "",
    credit: str = "",
    limit: int = 200,
    include_stories: bool = False,
    dry_run: bool = False,
) -> dict:
    """Importa fotografias da exportação oficial para os Quadros do acervo."""
    summary = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "found": 0,
        "error": "",
        "items": [],
    }
    staging = None
    try:
        export_root, staging = open_export(path)
        items = parse_export(export_root, include_stories=include_stories)
        if limit > 0:
            items = items[:limit]
        summary["found"] = len(items)
        summary["items"] = items
        resolved_credit = credit or archive_credit(handle or DEFAULT_INSTAGRAM_HANDLE)
        if dry_run:
            return summary
        for item in items:
            try:
                data = item.path.read_bytes()
            except OSError as exc:
                logger.warning("Falha ao ler %s: %s", item.path, exc)
                summary["skipped"] += 1
                continue
            if len(data) > 12 * 1024 * 1024:
                summary["skipped"] += 1
                continue
            extension = item.path.suffix.lower() or ".jpg"
            if extension == ".jpeg":
                extension = ".jpg"
            outcome = upsert_archive_frame(
                remote_id=item.remote_id,
                caption=item.caption,
                permalink="",
                taken_at=item.taken_at,
                credit=resolved_credit,
                image_bytes=data,
                extension=extension,
                alt_text=item.caption,
            )
            summary[outcome] += 1
        return summary
    except FileNotFoundError:
        summary["error"] = f"Caminho não encontrado: {path}"
        return summary
    except (ValueError, zipfile.BadZipFile) as exc:
        summary["error"] = str(exc)
        return summary
    finally:
        if staging is not None:
            staging.cleanup()
