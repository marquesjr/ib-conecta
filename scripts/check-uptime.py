#!/usr/bin/env python
"""Checagem HTTP do portal público (monitoramento externo, issue #36)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://www.ibsantaleopoldina.com.br"
USER_AGENT = "ib-conecta-uptime/1.0 (+https://github.com/marquesjr/ib-conecta)"
TIMEOUT_SECONDS = 25


def fetch(url: str) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        content_type = response.headers.get_content_type()
        return response.status, response.read(), content_type


def check_portal(base_url: str) -> None:
    base = base_url.rstrip("/")
    health_url = f"{base}/healthz/"
    status, body, _content_type = fetch(health_url)
    if status != 200:
        raise RuntimeError(f"{health_url} HTTP {status}")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{health_url} não devolveu JSON") from exc
    if payload.get("status") != "ok":
        raise RuntimeError(f"{health_url} payload inesperado: {payload}")
    print(f"ok {health_url} {payload}")

    home_url = f"{base}/"
    status, body, content_type = fetch(home_url)
    if status != 200:
        raise RuntimeError(f"{home_url} HTTP {status}")
    if content_type != "text/html":
        raise RuntimeError(
            f"{home_url} content-type {content_type!r}, esperado text/html"
        )
    if len(body) < 200:
        raise RuntimeError(f"{home_url} resposta HTML curta demais ({len(body)} bytes)")
    print(f"ok {home_url} HTTP {status} {len(body)} bytes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica se o portal público responde em HTTPS."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="URL canônica do portal (sem barra final)",
    )
    args = parser.parse_args()
    try:
        check_portal(args.url)
    except urllib.error.HTTPError as exc:
        print(f"DOWN HTTP {exc.code} {exc.reason} {exc.geturl()}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"DOWN {args.url}: {exc.reason}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI: qualquer falha é queda
        print(f"DOWN {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
