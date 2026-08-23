import re
from urllib.parse import quote

_PLANTON = r"plant[aã]o\s*24(?:\s*horas|h)?"
_DASH_NOTE = re.compile(
    rf"\s*[—–]\s*(?P<note>[^—–\n]*{_PLANTON}[^\n]*)\s*$",
    re.IGNORECASE,
)
_INLINE_NOTE = re.compile(
    rf"(?P<lead>.*?)(?:,|\s)+(?P<note>(?:não é um canal de {_PLANTON}|sem {_PLANTON})[.!]?)\s*$",
    re.IGNORECASE | re.DOTALL,
)
_LAST_SENTENCE_NOTE = re.compile(
    rf"(?P<lead>.*?[.!?])\s+(?P<note>[^.!?]*{_PLANTON}[^.!?]*[.!]?)\s*$",
    re.IGNORECASE | re.DOTALL,
)


def split_whatsapp_welcome(text: str | None) -> tuple[str, str]:
    """Split a 24h-duty disclaimer out of WhatsApp welcome copy.

    Returns (lead, note). If the CMS text has no plantão-24 clause, note is
    empty and the full string stays in lead — we do not invent a disclaimer.
    """
    raw = (text or "").strip()
    if not raw:
        return "", ""

    dash = _DASH_NOTE.search(raw)
    if dash:
        lead = raw[: dash.start()].strip().rstrip(" —–-")
        note = dash.group("note").strip()
        if lead and note:
            return lead, note

    for pattern in (_INLINE_NOTE, _LAST_SENTENCE_NOTE):
        match = pattern.search(raw)
        if match:
            lead = match.group("lead").strip().rstrip(" —–-")
            note = match.group("note").strip()
            if lead and note:
                return lead, note

    return raw, ""


def build_whatsapp_url(number: str, message: str = "") -> str:
    digits = "".join(ch for ch in (number or "") if ch.isdigit())
    if not digits:
        return ""
    url = f"https://wa.me/{digits}"
    if message:
        url = f"{url}?text={quote(message)}"
    return url


def build_whatsapp_share_url(title: str, url: str) -> str:
    page_url = (url or "").strip()
    if not page_url:
        return ""
    heading = (title or "").strip()
    text = f"{heading}\n{page_url}" if heading else page_url
    return f"https://wa.me/?text={quote(text)}"
