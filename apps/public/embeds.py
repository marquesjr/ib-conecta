"""Helpers for light external media embeds (YouTube etc.)."""

import re
from urllib.parse import parse_qs, urlparse

_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
}

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,}$")
_AUDIO_SUFFIXES = (".mp3", ".ogg", ".oga", ".m4a", ".aac", ".wav", ".opus")


def youtube_video_id(url: str) -> str:
    """Extract a YouTube video id from common watch/share/embed/live URLs."""
    if not url:
        return ""

    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    if host not in _YOUTUBE_HOSTS:
        return ""

    path = parsed.path or ""
    if host.endswith("youtu.be"):
        candidate = path.strip("/").split("/")[0]
        return candidate if _VIDEO_ID_RE.match(candidate) else ""

    for prefix in ("/embed/", "/shorts/", "/live/"):
        if path.startswith(prefix):
            rest = path[len(prefix) :].split("/")[0]
            return rest if _VIDEO_ID_RE.match(rest) else ""

    if path.startswith("/watch") or path == "/watch":
        values = parse_qs(parsed.query).get("v", [])
        candidate = values[0] if values else ""
        return candidate if _VIDEO_ID_RE.match(candidate) else ""

    return ""


def youtube_embed_src(url: str) -> str:
    """
    Build a privacy-friendly YouTube embed URL without autoplay.

    Returns empty string when the input is not a recognizable YouTube URL.
    """
    video_id = youtube_video_id(url)
    if not video_id:
        return ""
    return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"


def is_external_audio_url(url: str) -> bool:
    """True when URL points at a common audio file (streamed, not hosted here)."""
    if not url:
        return False
    path = urlparse(url.strip()).path.lower()
    return any(path.endswith(suffix) for suffix in _AUDIO_SUFFIXES)
