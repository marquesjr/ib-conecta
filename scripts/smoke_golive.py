#!/usr/bin/env python
"""Smoke test de go-live do portal em produção (issue #40).

Só faz GET anônimo: não envia formulário, não cria conta, não grava nada no banco.
Complementa ``check-uptime.py`` cobrindo HTTPS, redirects de domínio, páginas
públicas, formulários, login, área privada e CMS.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

DEFAULT_URL = "https://www.ibsantaleopoldina.com.br"
USER_AGENT = "ib-conecta-smoke/1.0 (+https://github.com/marquesjr/ib-conecta)"
TIMEOUT_SECONDS = 25


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: str

    def header(self, name: str) -> str:
        return self.headers.get(name.lower(), "")


Fetcher = Callable[[str], Response]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return None


def fetch(url: str) -> Response:
    """GET sem seguir redirects, para o smoke conferir o Location."""
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            status, headers, raw = response.status, response.headers, response.read()
    except urllib.error.HTTPError as exc:
        status, headers, raw = exc.code, exc.headers, exc.read()
    return Response(
        status=status,
        headers={key.lower(): value for key, value in headers.items()},
        body=raw.decode("utf-8", errors="replace"),
    )


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _expect_html(response: Response, *snippets: str) -> None:
    _expect(response.status == 200, f"HTTP {response.status}, esperado 200")
    _expect(
        response.header("content-type").startswith("text/html"),
        f"content-type {response.header('content-type')!r}, esperado text/html",
    )
    for snippet in snippets:
        _expect(snippet in response.body, f"HTML sem {snippet!r}")


def _expect_redirect(response: Response, target_prefix: str) -> None:
    _expect(
        response.status in {301, 302, 307, 308},
        f"HTTP {response.status}, esperado redirect",
    )
    location = response.header("location")
    _expect(
        location.startswith(target_prefix),
        f"Location {location!r}, esperado começar com {target_prefix!r}",
    )


def _form_page(response: Response) -> None:
    _expect_html(response, "<form", "csrfmiddlewaretoken")


def build_checks(base_url: str) -> list[tuple[str, str, Callable[[Response], None]]]:
    base = base_url.rstrip("/")
    parts = urllib.parse.urlsplit(base)
    host = parts.netloc
    apex = host.removeprefix("www.")
    checks: list[tuple[str, str, Callable[[Response], None]]] = []

    if parts.scheme == "https":
        checks.append(
            (
                "HTTP redireciona para HTTPS",
                f"http://{host}/",
                lambda r: _expect_redirect(r, f"https://{host}/"),
            )
        )
        if apex != host:
            checks.append(
                (
                    "Apex redireciona para www",
                    f"https://{apex}/planeje-sua-visita/",
                    lambda r: _expect_redirect(r, f"{base}/planeje-sua-visita/"),
                )
            )

    def healthz(response: Response) -> None:
        _expect(response.status == 200, f"HTTP {response.status}")
        _expect(json.loads(response.body).get("status") == "ok", response.body[:200])

    def home(response: Response) -> None:
        _expect_html(response, "<main")
        if parts.scheme == "https":
            _expect(
                response.header("x-content-type-options") == "nosniff",
                "sem X-Content-Type-Options: nosniff",
            )

    checks += [
        ("Health check (app + banco)", f"{base}/healthz/", healthz),
        ("Home", f"{base}/", home),
        ("Planeje sua visita", f"{base}/planeje-sua-visita/", _expect_html),
        ("Contribuições", f"{base}/contribuicoes/", _expect_html),
        ("Política de privacidade", f"{base}/privacidade/", _expect_html),
        ("Formulário: pedido de oração", f"{base}/pedido-de-oracao/", _form_page),
        ("Formulário: quero conhecer", f"{base}/quero-conhecer/", _form_page),
        ("Login", f"{base}/conta/entrar/", _form_page),
        (
            "Área privada exige login",
            f"{base}/area-privada/",
            lambda r: _expect_redirect(r, "/conta/entrar/"),
        ),
        (
            "Escalas exigem login",
            f"{base}/area-privada/ministerios/",
            lambda r: _expect_redirect(r, "/conta/entrar/"),
        ),
        (
            "CMS exige login",
            f"{base}/admin/",
            lambda r: _expect_redirect(r, "/admin/login/"),
        ),
        ("Login do CMS", f"{base}/admin/login/", _form_page),
    ]
    return checks


def run(base_url: str, fetcher: Fetcher = fetch) -> list[tuple[str, str, str | None]]:
    """Roda todas as checagens e devolve (nome, url, erro ou None)."""
    results = []
    for name, url, check in build_checks(base_url):
        try:
            check(fetcher(url))
            error = None
        except urllib.error.URLError as exc:
            error = f"sem resposta: {exc.reason}"
        except Exception as exc:  # noqa: BLE001 — smoke: qualquer falha reprova
            error = str(exc) or exc.__class__.__name__
        results.append((name, url, error))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test de go-live do portal.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL canônica (sem barra final)")
    args = parser.parse_args()

    results = run(args.url)
    for name, url, error in results:
        if error is None:
            print(f"ok    {name} ({url})")
        else:
            print(f"FALHA {name} ({url}): {error}")
    failures = sum(1 for *_, error in results if error)
    print(f"\n{len(results) - failures}/{len(results)} checagens ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
